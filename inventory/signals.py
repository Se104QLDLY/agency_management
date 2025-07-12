# signals.py
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Sum
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError

# Local models
from .models import (
    Item,
    IssueDetail,
    ReceiptDetail,
    Receipt,
    Issue,
)

# Cross-app import (placed inside ready() call via apps.py, safe here)
from agency.models import Agency

# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------


def _expected_line_total(quantity, unit_price) -> Decimal:
    """Calculate line_total = quantity × unit_price with 2-decimal rounding."""
    # Convert quantity to Decimal to handle string/int/float inputs
    try:
        # Handle various input types for quantity
        if isinstance(quantity, str):
            # Remove any non-numeric characters and convert
            quantity_str = ''.join(c for c in quantity if c.isdigit() or c == '.')
            quantity_decimal = Decimal(quantity_str) if quantity_str else Decimal('0')
        else:
            quantity_decimal = Decimal(str(quantity))
        
        # Handle various input types for unit_price
        if isinstance(unit_price, str):
            # Remove any non-numeric characters and convert
            unit_price_str = ''.join(c for c in unit_price if c.isdigit() or c == '.')
            unit_price_decimal = Decimal(unit_price_str) if unit_price_str else Decimal('0')
        else:
            unit_price_decimal = Decimal(str(unit_price))
        
        result = (quantity_decimal * unit_price_decimal).quantize(Decimal("0.01"))
        return result
        
    except Exception as e:
        raise


def _price_with_markup(base_price: Decimal) -> Decimal:
    """Return price after 102 % markup rounded to 2 decimals."""
    return (base_price * Decimal("1.02")).quantize(Decimal("0.01"), ROUND_HALF_UP)


# ---------------------------------------------------------------------
# 1.  PRE-SAVE — always fix line_total for consistency
# ---------------------------------------------------------------------


@receiver(pre_save, sender=ReceiptDetail)
def calc_line_total_receipt(sender, instance: ReceiptDetail, **kwargs):
    instance.line_total = _expected_line_total(instance.quantity, instance.unit_price)


@receiver(pre_save, sender=IssueDetail)
def calc_line_total_issue(sender, instance: IssueDetail, **kwargs):
    instance.line_total = _expected_line_total(instance.quantity, instance.unit_price)


# ---------------------------------------------------------------------
# 2.  POST-SAVE — business logic for stock & debt after INSERT
# ---------------------------------------------------------------------


@receiver(post_save, sender=ReceiptDetail)
def handle_receipt_detail_created(sender, instance: ReceiptDetail, created: bool, **kwargs):
    """Increase stock & update Receipt total when a new ReceiptDetail is created."""
    if not created:
        return

    with transaction.atomic():
        # 1. Increase stock
        item = Item.objects.select_for_update().get(pk=instance.item_id)
        item.stock_quantity += instance.quantity
        item.save(update_fields=["stock_quantity"])

        # 2. Re-calc receipt total_amount
        receipt_total = (
            ReceiptDetail.objects.filter(receipt_id=instance.receipt_id).aggregate(total=Sum("line_total"))[
                "total"
            ]
            or Decimal("0.00")
        )
        Receipt.objects.filter(pk=instance.receipt_id).update(total_amount=receipt_total)


@receiver(post_save, sender=IssueDetail)
def handle_issue_detail_created(sender, instance: IssueDetail, created: bool, **kwargs):
    """Calculate line totals and validate prices, but DON'T deduct stock or update debt yet."""
    if not created:
        return

    with transaction.atomic():
        # ------------------------------------------------------------
        # 1. Fetch related records with locking
        # ------------------------------------------------------------
        item = Item.objects.select_for_update().get(pk=instance.item_id)
        issue = Issue.objects.select_for_update().get(pk=instance.issue_id)

        # ------------------------------------------------------------
        # 2. Validate price markup (must equal 102 % of base price)
        # ------------------------------------------------------------
        expected_price = _price_with_markup(item.price)
        # Allow small floating point precision difference (within 0.01)
        price_diff = abs(instance.unit_price - expected_price)
        if price_diff > Decimal('0.01'):
            raise ValidationError(f"Giá xuất phải bằng 102% giá nhập. Mong đợi: {expected_price}, Nhận được: {instance.unit_price}")

        # ------------------------------------------------------------
        # 3. Validate stock availability (but don't deduct yet)
        # ------------------------------------------------------------
        if item.stock_quantity < instance.quantity:
            raise ValidationError("Không đủ hàng trong kho để xuất.")

        # ------------------------------------------------------------
        # 4. Update Issue total_amount only
        # ------------------------------------------------------------
        issue_total = (
            IssueDetail.objects.filter(issue_id=instance.issue_id).aggregate(total=Sum("line_total"))[
                "total"
            ]
            or Decimal("0.00")
        )
        Issue.objects.filter(pk=instance.issue_id).update(total_amount=issue_total)

        # ------------------------------------------------------------
        # 5. Validate debt limit (but don't update debt yet)
        # ------------------------------------------------------------
        agency = issue.agency if hasattr(issue, 'agency') else None
        if not agency:
            from agency.models import Agency
            agency = Agency.objects.select_related('agency_type').get(pk=issue.agency_id)
            
        current_debt = agency.debt_amount or Decimal("0.00")
        max_debt = agency.agency_type.max_debt
        
        # Check if confirming this issue would exceed debt limit
        if issue.status == 'processing':
            potential_new_debt = current_debt + issue_total
            if potential_new_debt > max_debt:
                raise ValidationError("Xác nhận đơn hàng này sẽ vượt giới hạn nợ của đại lý.")

        # NOTE: Stock deduction and debt update will happen when status changes to 'confirmed'


# ---------------------------------------------------------------------
# 3.  POST-DELETE / POST-SAVE on Detail — recalc totals (already covered)
# ---------------------------------------------------------------------

# (Functions update_receipt_total / update_issue_total kept for reuse)

def update_receipt_total(receipt_id):
    receipt = Receipt.objects.get(pk=receipt_id)
    total = receipt.details.aggregate(total=Sum('line_total'))['total'] or 0
    receipt.total_amount = total
    receipt.save(update_fields=["total_amount"])

def update_issue_total(issue_id):
    issue = Issue.objects.get(pk=issue_id)
    total = issue.details.aggregate(total=Sum('line_total'))['total'] or 0
    issue.total_amount = total
    issue.save(update_fields=["total_amount"])

@receiver([post_save, post_delete], sender=ReceiptDetail)
def recalc_receipt_total(sender, instance, **kwargs):
    update_receipt_total(instance.receipt_id)

@receiver([post_save, post_delete], sender=IssueDetail)
def recalc_issue_total(sender, instance, **kwargs):
    update_issue_total(instance.issue_id)


# ---------------------------------------------------------------------
# 4. ISSUE STATUS CHANGE - Handle stock deduction and debt updates
# ---------------------------------------------------------------------

@receiver(post_save, sender=Issue)
def handle_issue_status_change(sender, instance: Issue, created: bool, **kwargs):
    """Handle stock deduction and debt update when issue status changes to 'delivered'."""
    
    # Skip on creation - only handle status changes
    if created:
        return
        
    # Only process when status becomes 'delivered' (agency confirms delivery)
    if instance.status != 'delivered':
        return
        
    # Check if this status change was already processed
    # (to avoid double-processing in case of multiple saves)
    if hasattr(instance, '_status_processed'):
        return
        
    with transaction.atomic():
        # Mark as processed to avoid double-processing
        instance._status_processed = True
        
        # Get agency with lock
        from agency.models import Agency
        agency = Agency.objects.select_for_update().get(pk=instance.agency_id)
        
        # Track whether we need to rollback if any step fails
        stock_updates = []
        
        try:
            # 1. Deduct stock for all issue details
            for detail in instance.details.all():
                item = Item.objects.select_for_update().get(pk=detail.item_id)
                
                # Final stock validation before deduction
                if item.stock_quantity < detail.quantity:
                    raise ValidationError(
                        f"Không đủ hàng trong kho cho sản phẩm {item.item_name}. "
                        f"Yêu cầu: {detail.quantity}, Còn lại: {item.stock_quantity}"
                    )
                
                # Store original values for potential rollback
                original_stock = item.stock_quantity
                
                # Deduct stock
                item.stock_quantity -= detail.quantity
                item.save(update_fields=["stock_quantity"])
                
                # Track for potential rollback
                stock_updates.append({
                    'item': item,
                    'original_stock': original_stock,
                    'deducted': detail.quantity
                })
            
            # 2. Update agency debt
            original_debt = agency.debt_amount
            new_debt = (agency.debt_amount or Decimal("0.00")) + instance.total_amount
            
            # Final debt limit validation
            if new_debt > agency.agency_type.max_debt:
                # Rollback stock changes
                for update in stock_updates:
                    update['item'].stock_quantity = update['original_stock']
                    update['item'].save(update_fields=["stock_quantity"])
                
                raise ValidationError(
                    f"Xác nhận đơn hàng sẽ vượt giới hạn nợ. "
                    f"Nợ hiện tại: {original_debt}, Giới hạn: {agency.agency_type.max_debt}, "
                    f"Tổng sau xác nhận: {new_debt}"
                )
            
            # Update debt
            agency.debt_amount = new_debt
            agency.save(update_fields=["debt_amount"])
            
        except Exception as e:
            # Rollback any stock changes if debt update fails
            for update in stock_updates:
                update['item'].stock_quantity = update['original_stock']
                update['item'].save(update_fields=["stock_quantity"])
            raise e