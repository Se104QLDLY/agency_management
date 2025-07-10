from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum, Max
from authentication.exceptions import DebtLimitExceeded, OutOfStock
from agency.models import Agency
from .models import Item, Receipt, ReceiptDetail, Issue, IssueDetail
import logging

logger = logging.getLogger(__name__)

class InventoryService:
    """
    Business logic service for inventory operations
    Implements stock management and debt validation per docs/flow.md
    """
    
    @staticmethod
    @transaction.atomic
    def create_receipt(receipt_data, user):
        """
        Create stock-in receipt with automatic stock updates
        Per docs/flow.md: Receipt → Stock +
        """
        # Extract items data
        items_data = receipt_data.pop('items', [])
        
        # Create receipt
        receipt = Receipt.objects.create(
            agency_id=receipt_data['agency_id'],
            user_id=user.user_id,
            receipt_date=receipt_data.get('receipt_date', timezone.now().date()),
            total_amount=Decimal('0.00')
        )
        
        total_amount = Decimal('0.00')
        
        # Create receipt details and update stock
        for item_data in items_data:
            item = Item.objects.get(item_id=item_data['item_id'])
            
            line_total = Decimal(item_data['quantity']) * Decimal(item_data.get('unit_price', item.price))
            
            # Create receipt detail
            ReceiptDetail.objects.create(
                receipt=receipt,
                item=item,
                quantity=item_data['quantity'],
                unit_price=item_data.get('unit_price', item.price),
                line_total=line_total
            )
            
            # Update stock quantity
            item.stock_quantity += item_data['quantity']
            item.save()
            
            total_amount += line_total
        
        # Update receipt total
        receipt.total_amount = total_amount
        receipt.save()
        
        return receipt
    
    @staticmethod
    @transaction.atomic
    def create_issue(issue_data, user):
        """
        Create stock-out issue request (without stock validation)
        Agency can submit requests regardless of stock availability
        Stock validation will be done during staff approval
        """
        agency_id = issue_data['agency_id']
        # Determine next primary key manually to avoid duplicate key errors without changing DDL
        current_max = Issue.objects.aggregate(max_id=Max('issue_id'))['max_id'] or 0
        next_id = current_max + 1
        items_data = issue_data.pop('items', [])
        
        # Get agency with debt info
        try:
            agency = Agency.objects.select_related('agency_type').get(agency_id=agency_id)
        except Agency.DoesNotExist:
            raise ValueError(f"Agency {agency_id} not found")
        
        # Calculate total issue amount (for debt validation)
        total_amount = Decimal('0.00')
        item_validations = []
        
        for item_data in items_data:
            # Support both 'item_id' and 'item' keys
            item_id = item_data.get('item_id', item_data.get('item'))
            try:
                item = Item.objects.get(item_id=item_id)
            except Item.DoesNotExist:
                raise ValueError(f"Item {item_id} not found")
            
            quantity = item_data.get('quantity')
            unit_price = item_data.get('unit_price', item.price)
            line_total = Decimal(quantity) * Decimal(unit_price)
            
            # NOTE: Stock validation removed - will be done during approval
            
            item_validations.append({
                'item': item,
                'quantity': quantity,
                'unit_price': unit_price,
                'line_total': line_total
            })
            
            total_amount += line_total
        
        # Validate debt limit only
        current_debt = agency.debt_amount
        max_debt = agency.agency_type.max_debt
        new_debt = current_debt + total_amount
        
        if new_debt > max_debt:
            raise DebtLimitExceeded(
                current_debt=current_debt,
                max_debt=max_debt,
                additional_amount=total_amount
            )
        
        # Create issue in 'processing' status (pending staff approval)
        issue_date = issue_data.get('issue_date', timezone.now().date())
        issue = Issue(
            issue_id=next_id,
            agency_id=agency_id,
            user_id=user.user_id,
            issue_date=issue_date,
            total_amount=total_amount,
            status='processing'  # Default status for new requests
        )
        # force_insert to respect manual PK
        issue.save(force_insert=True)
        
        # Create issue details but DON'T update stock yet
        current_max_detail = IssueDetail.objects.aggregate(max_id=Max('issue_detail_id'))['max_id'] or 0
        next_detail_id = current_max_detail + 1
        
        for validation in item_validations:
            item = validation['item']
            
            # Create issue detail with manual primary key
            detail = IssueDetail(
                issue_detail_id=next_detail_id,
                issue=issue,
                item=item,
                quantity=validation['quantity'],
                unit_price=validation['unit_price'],
                line_total=validation['line_total']
            )
            detail.save(force_insert=True)
            next_detail_id += 1
            
            # NOTE: Stock deduction removed - will be done during approval
        
        # NOTE: Debt update removed - will be done during approval
        
        return issue
    
    @staticmethod
    def get_low_stock_items(threshold=10):
        """Get items with stock below threshold"""
        return Item.objects.filter(stock_quantity__lt=threshold).order_by('stock_quantity')
    
    @staticmethod
    def get_item_stock_history(item_id, start_date=None, end_date=None):
        """Get stock movement history for an item"""
        receipts = ReceiptDetail.objects.filter(item_id=item_id)
        issues = IssueDetail.objects.filter(item_id=item_id)
        
        if start_date:
            receipts = receipts.filter(receipt__receipt_date__gte=start_date)
            issues = issues.filter(issue__issue_date__gte=start_date)
        
        if end_date:
            receipts = receipts.filter(receipt__receipt_date__lte=end_date)
            issues = issues.filter(issue__issue_date__lte=end_date)
        
        history = []
        
        # Add receipts (positive movements)
        for detail in receipts.select_related('receipt'):
            history.append({
                'date': detail.receipt.receipt_date,
                'type': 'RECEIPT',
                'quantity': detail.quantity,
                'reference_id': detail.receipt.receipt_id,
                'agency_id': detail.receipt.agency_id
            })
        
        # Add issues (negative movements)
        for detail in issues.select_related('issue'):
            history.append({
                'date': detail.issue.issue_date,
                'type': 'ISSUE',
                'quantity': -detail.quantity,  # Negative for issues
                'reference_id': detail.issue.issue_id,
                'agency_id': detail.issue.agency_id
            })
        
        # Sort by date
        history.sort(key=lambda x: x['date'], reverse=True)
        
        return history
    
    @staticmethod
    @transaction.atomic
    def approve_issue(issue, approved_by_user):
        """
        Approve issue request - this now only changes status.
        Stock deduction and debt update will be handled by signals.
        """
        try:
            if issue.status != 'processing':
                raise ValueError(f"Cannot approve issue with status '{issue.status}'. Only 'processing' issues can be approved.")

            # Get agency for validation
            agency = Agency.objects.select_related('agency_type').get(agency_id=issue.agency_id)

            # Pre-validate stock availability for all items
            stock_issues = []
            for detail in issue.details.all():
                if detail.item.stock_quantity < detail.quantity:
                    stock_issues.append({
                        'item_name': detail.item.item_name,
                        'requested': detail.quantity,
                        'available': detail.item.stock_quantity
                    })

            if stock_issues:
                # Build detailed error message
                error_msg = "Insufficient stock for the following items:\n"
                for issue_item in stock_issues:
                    error_msg += f"- {issue_item['item_name']}: requested {issue_item['requested']}, available {issue_item['available']}\n"
                logger.error(f"[approve_issue] OutOfStock: {error_msg}")
                raise OutOfStock(error_msg)

            # Pre-validate debt limit
            new_debt = agency.debt_amount + issue.total_amount
            if new_debt > agency.agency_type.max_debt:
                logger.error(f"[approve_issue] DebtLimitExceeded: Approving this issue would exceed debt limit. Current debt: {agency.debt_amount}, Limit: {agency.agency_type.max_debt}, Total after approval: {new_debt}")
                raise ValueError(
                    f"Approving this issue would exceed debt limit. "
                    f"Current debt: {agency.debt_amount}, Limit: {agency.agency_type.max_debt}, "
                    f"Total after approval: {new_debt}"
                )

            # Change status to 'confirmed' - signals will handle stock deduction and debt update
            issue.status = 'confirmed'
            issue.save(update_fields=['status'])
            logger.info(f"[approve_issue] Issue {issue.issue_id} approved by user {approved_by_user}. Status set to confirmed.")
            return issue
        except Exception as e:
            logger.exception(f"[approve_issue] Exception: {e}")
            raise

    @staticmethod
    @transaction.atomic
    def reject_issue(issue, rejected_by_user, rejection_reason=None):
        """
        Reject issue request
        Called when staff rejects a pending issue request
        """
        try:
            if issue.status != 'processing':
                raise ValueError(f"Cannot reject issue with status '{issue.status}'. Only 'processing' issues can be rejected.")

            # Update issue status
            issue.status = 'cancelled'
            issue.status_reason = rejection_reason or 'Rejected by staff'
            issue.save()
            logger.info(f"[reject_issue] Issue {issue.issue_id} rejected by user {rejected_by_user}. Reason: {issue.status_reason}")
            return issue
        except Exception as e:
            logger.exception(f"[reject_issue] Exception: {e}")
            raise

class StockCalculationService:
    """Service for calculating stock levels and movements"""
    
    @staticmethod
    def calculate_current_stock(item_id):
        """Calculate current stock level from movements"""
        from django.db.models import Sum
        
        # Sum all receipts
        total_receipts = ReceiptDetail.objects.filter(
            item_id=item_id
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Sum all issues
        total_issues = IssueDetail.objects.filter(
            item_id=item_id
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        return total_receipts - total_issues
    
    @staticmethod
    def validate_stock_consistency():
        """Validate that calculated stock matches stored stock"""
        inconsistencies = []
        
        for item in Item.objects.all():
            calculated_stock = StockCalculationService.calculate_current_stock(item.item_id)
            
            if calculated_stock != item.stock_quantity:
                inconsistencies.append({
                    'item_id': item.item_id,
                    'item_name': item.item_name,
                    'stored_stock': item.stock_quantity,
                    'calculated_stock': calculated_stock,
                    'difference': calculated_stock - item.stock_quantity
                })
        
        return inconsistencies