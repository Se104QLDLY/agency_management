from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from authentication.exceptions import DebtLimitExceeded, OutOfStock
from agency.models import Agency
from .models import Item, Receipt, ReceiptDetail, Issue, IssueDetail


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
        Create stock-out issue with debt and stock validation
        Per docs/flow.md: Validate debt limit → Check stock → Issue → Update debt
        """
        agency_id = issue_data['agency_id']
        items_data = issue_data.pop('items', [])
        
        # Get agency with debt info
        try:
            agency = Agency.objects.select_related('agency_type').get(agency_id=agency_id)
        except Agency.DoesNotExist:
            raise ValueError(f"Agency {agency_id} not found")
        
        # Calculate total issue amount
        total_amount = Decimal('0.00')
        item_validations = []
        
        for item_data in items_data:
            try:
                item = Item.objects.get(item_id=item_data['item_id'])
            except Item.DoesNotExist:
                raise ValueError(f"Item {item_data['item_id']} not found")
            
            quantity = item_data['quantity']
            unit_price = item_data.get('unit_price', item.price)
            line_total = Decimal(quantity) * Decimal(unit_price)
            
            # Validate stock availability
            if item.stock_quantity < quantity:
                raise OutOfStock(
                    item_name=item.item_name,
                    requested_qty=quantity,
                    available_qty=item.stock_quantity
                )
            
            item_validations.append({
                'item': item,
                'quantity': quantity,
                'unit_price': unit_price,
                'line_total': line_total
            })
            
            total_amount += line_total
        
        # Validate debt limit
        current_debt = agency.debt_amount
        max_debt = agency.agency_type.max_debt
        new_debt = current_debt + total_amount
        
        if new_debt > max_debt:
            raise DebtLimitExceeded(
                current_debt=current_debt,
                max_debt=max_debt,
                additional_amount=total_amount
            )
        
        # All validations passed - create issue
        issue = Issue.objects.create(
            agency_id=agency_id,
            user_id=user.user_id,
            issue_date=issue_data.get('issue_date', timezone.now().date()),
            total_amount=total_amount
        )
        
        # Create issue details and update stock
        for validation in item_validations:
            item = validation['item']
            
            # Create issue detail
            IssueDetail.objects.create(
                issue=issue,
                item=item,
                quantity=validation['quantity'],
                unit_price=validation['unit_price'],
                line_total=validation['line_total']
            )
            
            # Update stock quantity (reduce)
            item.stock_quantity -= validation['quantity']
            item.save()
        
        # Update agency debt
        agency.debt_amount = new_debt
        agency.save()
        
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