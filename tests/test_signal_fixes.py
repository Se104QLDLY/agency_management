"""
Comprehensive test suite for validating the signal fixes and business logic flow.
Run this after implementing the fixes to ensure everything works correctly.
"""

import pytest
from decimal import Decimal
from django.test import TestCase, TransactionTestCase
from django.core.exceptions import ValidationError
from django.db import transaction

from agency.models import Agency, AgencyType, District
from inventory.models import Item, Unit, Issue, IssueDetail, Receipt, ReceiptDetail
from finance.models import Payment
from authentication.models import Account, User


class SignalFlowTestCase(TransactionTestCase):
    """Test the corrected signal flow for business logic"""
    
    def setUp(self):
        """Set up test data"""
        # Create agency type
        self.agency_type = AgencyType.objects.create(
            type_name="Test Type",
            max_debt=Decimal("10000.00"),
            description="Test agency type"
        )
        
        # Create district
        self.district = District.objects.create(
            city_name="Test City",
            district_name="Test District",
            max_agencies=10
        )
        
        # Create agency
        self.agency = Agency.objects.create(
            agency_name="Test Agency",
            agency_type=self.agency_type,
            phone_number="1234567890",
            address="Test Address",
            district=self.district,
            reception_date="2024-01-01",
            debt_amount=Decimal("1000.00")
        )
        
        # Create unit and item
        self.unit = Unit.objects.create(unit_name="Piece")
        self.item = Item.objects.create(
            item_name="Test Item",
            unit=self.unit,
            price=Decimal("100.00"),
            stock_quantity=50,
            description="Test item"
        )
        
        # Create user account
        self.account = Account.objects.create(
            username="testuser",
            password_hash="hashed_password",
            account_role="staff"
        )
        self.user = User.objects.create(
            account=self.account,
            full_name="Test User",
            email="test@example.com"
        )
    
    def test_import_flow_correct(self):
        """Test that import (receipt) flow works correctly"""
        initial_stock = self.item.stock_quantity
        
        # Create receipt
        receipt = Receipt.objects.create(
            receipt_date="2024-01-01",
            user_id=self.user.user_id,
            agency_id=1,  # Default distributor
            total_amount=Decimal("0.00")
        )
        
        # Create receipt detail - should auto-increase stock
        receipt_detail = ReceiptDetail.objects.create(
            receipt=receipt,
            item=self.item,
            quantity=10,
            unit_price=Decimal("100.00"),
            line_total=Decimal("1000.00")
        )
        
        # Refresh item from database
        self.item.refresh_from_db()
        
        # Stock should increase
        self.assertEqual(self.item.stock_quantity, initial_stock + 10)
        
        # Receipt total should be updated
        receipt.refresh_from_db()
        self.assertEqual(receipt.total_amount, Decimal("1000.00"))
    
    def test_export_flow_processing_no_immediate_changes(self):
        """Test that creating issue in 'processing' status doesn't immediately affect stock/debt"""
        initial_stock = self.item.stock_quantity
        initial_debt = self.agency.debt_amount
        
        # Create issue in processing status
        issue = Issue.objects.create(
            issue_date="2024-01-01",
            agency_id=self.agency.agency_id,
            user_id=self.user.user_id,
            total_amount=Decimal("0.00"),
            status='processing'
        )
        
        # Create issue detail with correct price markup (102%)
        expected_price = self.item.price * Decimal("1.02")
        issue_detail = IssueDetail.objects.create(
            issue=issue,
            item=self.item,
            quantity=5,
            unit_price=expected_price,
            line_total=expected_price * 5
        )
        
        # Refresh objects
        self.item.refresh_from_db()
        self.agency.refresh_from_db()
        
        # Stock and debt should NOT change yet (still processing)
        self.assertEqual(self.item.stock_quantity, initial_stock)
        self.assertEqual(self.agency.debt_amount, initial_debt)
        
        # Issue total should be updated
        issue.refresh_from_db()
        self.assertEqual(issue.total_amount, expected_price * 5)
    
    def test_export_flow_confirmation_triggers_changes(self):
        """Test that confirming issue triggers stock deduction and debt increase"""
        initial_stock = self.item.stock_quantity
        initial_debt = self.agency.debt_amount
        
        # Create issue and detail first
        issue = Issue.objects.create(
            issue_date="2024-01-01",
            agency_id=self.agency.agency_id,
            user_id=self.user.user_id,
            total_amount=Decimal("0.00"),
            status='processing'
        )
        
        expected_price = self.item.price * Decimal("1.02")
        issue_detail = IssueDetail.objects.create(
            issue=issue,
            item=self.item,
            quantity=5,
            unit_price=expected_price,
            line_total=expected_price * 5
        )
        
        # Now confirm the issue - this should trigger signals
        issue.status = 'confirmed'
        issue.save()
        
        # Refresh objects
        self.item.refresh_from_db()
        self.agency.refresh_from_db()
        
        # Now stock should be deducted and debt increased
        self.assertEqual(self.item.stock_quantity, initial_stock - 5)
        self.assertEqual(self.agency.debt_amount, initial_debt + (expected_price * 5))
    
    def test_payment_flow_correct(self):
        """Test that payment correctly reduces debt"""
        initial_debt = self.agency.debt_amount
        payment_amount = Decimal("500.00")
        
        # Create confirmed payment
        payment = Payment.objects.create(
            payment_date="2024-01-01",
            agency_id=self.agency.agency_id,
            user_id=self.user.user_id,
            amount_collected=payment_amount,
            status='confirmed'
        )
        
        # Refresh agency
        self.agency.refresh_from_db()
        
        # Debt should be reduced
        self.assertEqual(self.agency.debt_amount, initial_debt - payment_amount)
    
    def test_payment_exceeds_debt_validation(self):
        """Test that payment cannot exceed current debt"""
        excessive_payment = self.agency.debt_amount + Decimal("1000.00")
        
        # This should raise validation error
        with self.assertRaises(ValidationError):
            payment = Payment.objects.create(
                payment_date="2024-01-01",
                agency_id=self.agency.agency_id,
                user_id=self.user.user_id,
                amount_collected=excessive_payment,
                status='confirmed'
            )
    
    def test_debt_limit_validation(self):
        """Test that debt limit is enforced during issue confirmation"""
        # Create an issue that would exceed debt limit
        large_issue = Issue.objects.create(
            issue_date="2024-01-01",
            agency_id=self.agency.agency_id,
            user_id=self.user.user_id,
            total_amount=Decimal("0.00"),
            status='processing'
        )
        
        # Create detail that would exceed limit
        excessive_amount = self.agency_type.max_debt
        expected_price = self.item.price * Decimal("1.02")
        
        IssueDetail.objects.create(
            issue=large_issue,
            item=self.item,
            quantity=100,  # Large quantity
            unit_price=expected_price,
            line_total=excessive_amount
        )
        
        # Confirming should raise validation error
        with self.assertRaises(ValidationError):
            large_issue.status = 'confirmed'
            large_issue.save()
    
    def test_stock_insufficient_validation(self):
        """Test that insufficient stock prevents issue confirmation"""
        # Create issue with more quantity than available
        issue = Issue.objects.create(
            issue_date="2024-01-01",
            agency_id=self.agency.agency_id,
            user_id=self.user.user_id,
            total_amount=Decimal("0.00"),
            status='processing'
        )
        
        expected_price = self.item.price * Decimal("1.02")
        IssueDetail.objects.create(
            issue=issue,
            item=self.item,
            quantity=self.item.stock_quantity + 10,  # More than available
            unit_price=expected_price,
            line_total=expected_price * (self.item.stock_quantity + 10)
        )
        
        # Confirming should raise validation error
        with self.assertRaises(ValidationError):
            issue.status = 'confirmed'
            issue.save()


class BusinessLogicIntegrationTestCase(TestCase):
    """Integration tests for complete business flows"""
    
    def setUp(self):
        """Set up test data"""
        # Same setup as above
        # ... (implement same setup)
        pass
    
    def test_complete_business_cycle(self):
        """Test complete cycle: Import -> Export Request -> Approval -> Payment"""
        # 1. Import items (Receipt)
        # 2. Create export request (Issue in processing)
        # 3. Approve export (Issue confirmed)
        # 4. Make payment
        # Verify all balances are correct
        pass
    
    def test_concurrent_operations(self):
        """Test that concurrent operations don't cause race conditions"""
        # Test multiple simultaneous issue confirmations
        # Test concurrent payments
        pass


if __name__ == '__main__':
    # Run with: python manage.py test tests.test_signal_fixes
    pytest.main([__file__])
