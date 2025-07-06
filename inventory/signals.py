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
    """Validate markup & stock, decrease stock, update Issue total & agency debt."""
    if not created:
        return

    with transaction.atomic():
        # ------------------------------------------------------------
        # 1. Fetch related records with locking
        # ------------------------------------------------------------
        item = Item.objects.select_for_update().get(pk=instance.item_id)
        issue = Issue.objects.select_for_update().get(pk=instance.issue_id)
        agency = Agency.objects.select_for_update().get(pk=issue.agency_id)
        agency_type = agency.agency_type  # has max_debt

        # ------------------------------------------------------------
        # 2. Validate price markup (must equal 102 % of base price)
        # ------------------------------------------------------------
        expected_price = _price_with_markup(item.price)
        if instance.unit_price != expected_price:
            raise ValidationError("Giá xuất phải bằng 102% giá nhập")

        # ------------------------------------------------------------
        # 3. Validate & update stock
        # ------------------------------------------------------------
        if item.stock_quantity < instance.quantity:
            raise ValidationError("Không đủ hàng trong kho để xuất.")

        item.stock_quantity -= instance.quantity
        item.save(update_fields=["stock_quantity"])

        # ------------------------------------------------------------
        # 4. Update Issue total_amount
        # ------------------------------------------------------------
        issue_total = (
            IssueDetail.objects.filter(issue_id=instance.issue_id).aggregate(total=Sum("line_total"))[
                "total"
            ]
            or Decimal("0.00")
        )
        Issue.objects.filter(pk=instance.issue_id).update(total_amount=issue_total)

        # ------------------------------------------------------------
        # 5. Update Agency debt & enforce limit
        # ------------------------------------------------------------
        new_debt = (agency.debt_amount or Decimal("0.00")) + instance.line_total
        if new_debt > agency_type.max_debt:
            raise ValidationError("Vượt giới hạn nợ của đại lý.")

        agency.debt_amount = new_debt
        agency.save(update_fields=["debt_amount"])


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