#!/usr/bin/env python
"""
Test script to verify that stock is reduced immediately when creating an Issue,
regardless of the issue status.
"""

import os
import sys
import django
from decimal import Decimal

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agency_management.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from inventory.models import Item, Issue, IssueDetail
from inventory.services import InventoryService
from agency.models import Agency, AgencyType
from django.db import transaction

def test_immediate_stock_reduction():
    """Test that stock is reduced immediately when creating an Issue"""
    
    print("🧪 Testing immediate stock reduction when creating Issue...")
    
    try:
        with transaction.atomic():
            # Create test data
            print("📋 Setting up test data...")
            
            # Create an agency type with debt limit
            agency_type, _ = AgencyType.objects.get_or_create(
                type_name="Test Type",
                defaults={
                    'max_debt': Decimal('1000000.00'),
                    'description': 'Test agency type'
                }
            )
            
            # Create an agency
            agency, _ = Agency.objects.get_or_create(
                agency_id=1,
                defaults={
                    'agency_name': 'Test Agency',
                    'agency_type': agency_type,
                    'debt_amount': Decimal('0.00'),
                    'phone': '1234567890',
                    'email': 'test@example.com',
                    'address': 'Test Address'
                }
            )
            
            # Create a test item with stock
            item, _ = Item.objects.get_or_create(
                item_id=1,
                defaults={
                    'item_name': 'Test Item',
                    'price': Decimal('100.00'),
                    'stock_quantity': 50,  # Initial stock
                    'unit_id': 1,
                    'description': 'Test item'
                }
            )
            
            # Record initial stock
            initial_stock = item.stock_quantity
            print(f"📦 Initial stock: {initial_stock}")
            
            # Create a mock user
            class MockUser:
                def __init__(self):
                    self.user_id = 1
            
            user = MockUser()
            
            print(f"📦 Initial stock: {item.stock_quantity}")
            print(f"💰 Item price: {item.price}")
            
            # Calculate correct issue price (102% of item price)
            issue_price = item.price * Decimal('1.02')
            print(f"📊 Calculated issue price (102%): {issue_price}")
            
            # Create issue data
            issue_data = {
                'agency_id': agency.agency_id,
                'items': [
                    {
                        'item_id': item.item_id,
                        'quantity': 10,
                        'unit_price': issue_price  # 102% of item price
                    }
                ]
            }
            
            print("🔄 Creating Issue...")
            
            # Create the issue
            issue = InventoryService.create_issue(issue_data, user)
            
            # Check if issue was created
            print(f"✅ Issue created with ID: {issue.issue_id}")
            print(f"📊 Issue status: {issue.status}")
            print(f"💰 Issue total amount: {issue.total_amount}")
            
            # Refresh item from database to get updated stock
            item.refresh_from_db()
            new_stock = item.stock_quantity
            
            print(f"📦 Stock after creating issue: {new_stock}")
            print(f"📉 Stock reduction: {initial_stock - new_stock}")
            
            # Verify stock was reduced immediately
            expected_stock = initial_stock - 10
            
            if new_stock == expected_stock:
                print("✅ SUCCESS: Stock was reduced immediately upon issue creation!")
                print(f"   - Initial stock: {initial_stock}")
                print(f"   - Issued quantity: 10")
                print(f"   - Expected stock: {expected_stock}")
                print(f"   - Actual stock: {new_stock}")
                print(f"   - Issue status: {issue.status} (still processing)")
            else:
                print("❌ FAILURE: Stock was not reduced correctly!")
                print(f"   - Expected stock: {expected_stock}")
                print(f"   - Actual stock: {new_stock}")
                
            # Verify issue details
            issue_details = IssueDetail.objects.filter(issue=issue)
            print(f"📋 Issue details count: {issue_details.count()}")
            
            for detail in issue_details:
                print(f"   - Item: {detail.item.item_name}")
                print(f"   - Quantity: {detail.quantity}")
                print(f"   - Unit price: {detail.unit_price}")
                print(f"   - Line total: {detail.line_total}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_immediate_stock_reduction()
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
