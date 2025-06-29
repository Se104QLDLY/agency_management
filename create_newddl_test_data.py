#!/usr/bin/env python3
"""
Test data creator for newddl.sql schema format
Creates minimal test data to verify backend functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agency_management.settings')
django.setup()

from authentication.models import Account, User
from agency.models import AgencyType, District, Agency, StaffAgency  
from inventory.models import Unit, Item, Receipt, ReceiptDetail, Issue, IssueDetail
from finance.models import Payment, Report
from regulation.models import Regulation
from django.utils import timezone
from decimal import Decimal

def create_test_data():
    print("🚀 Creating test data for newddl.sql format...")
    
    # 1. Create Accounts & Users
    print("📝 Creating accounts and users...")
    
    admin_account, _ = Account.objects.get_or_create(
        username='admin',
        defaults={
            'password_hash': 'scrypt:32768:8:1$2b2KsyDhdXhpJelc$eb9f9658e7c6a2b92a7b8b1c7f4d6e8a9c2b5d3f8e7a6c4e9b2a5c8f7d1e3b6a9c4f2d7e8b1a5c9f6d3e7b2a8c',
            'account_role': 'admin'
        }
    )
    
    staff_account, _ = Account.objects.get_or_create(
        username='staff1',
        defaults={
            'password_hash': 'scrypt:32768:8:1$2b2KsyDhdXhpJelc$eb9f9658e7c6a2b92a7b8b1c7f4d6e8a9c2b5d3f8e7a6c4e9b2a5c8f7d1e3b6a9c4f2d7e8b1a5c9f6d3e7b2a8c',
            'account_role': 'staff'
        }
    )
    
    agent_account, _ = Account.objects.get_or_create(
        username='agent1',
        defaults={
            'password_hash': 'scrypt:32768:8:1$2b2KsyDhdXhpJelc$eb9f9658e7c6a2b92a7b8b1c7f4d6e8a9c2b5d3f8e7a6c4e9b2a5c8f7d1e3b6a9c4f2d7e8b1a5c9f6d3e7b2a8c',
            'account_role': 'agent'
        }
    )
    
    admin_user, _ = User.objects.get_or_create(
        user_id=1,
        defaults={
            'account_id': admin_account.account_id,
            'full_name': 'Quản trị viên hệ thống',
            'email': 'admin@company.com',
            'phone_number': '0123456789',
            'address': 'TP.HCM'
        }
    )
    
    staff_user, _ = User.objects.get_or_create(
        user_id=2,
        defaults={
            'account_id': staff_account.account_id,
            'full_name': 'Nhân viên kinh doanh',
            'email': 'staff1@company.com',
            'phone_number': '0987654321',
            'address': 'Hà Nội'
        }
    )
    
    agent_user, _ = User.objects.get_or_create(
        user_id=3,
        defaults={
            'account_id': agent_account.account_id,
            'full_name': 'Đại lý test',
            'email': 'agent1@company.com',
            'phone_number': '0123987654',
            'address': 'Đà Nẵng'
        }
    )
    
    # 2. Create Agency Types & Districts
    print("🏢 Creating agency types and districts...")
    
    agency_type1, _ = AgencyType.objects.get_or_create(
        type_name='Đại lý cấp 1',
        defaults={
            'max_debt': Decimal('1000000000.00'),
            'description': 'Đại lý cấp 1 với hạn mức nợ cao'
        }
    )
    
    agency_type2, _ = AgencyType.objects.get_or_create(
        type_name='Đại lý cấp 2',
        defaults={
            'max_debt': Decimal('500000000.00'),
            'description': 'Đại lý cấp 2 với hạn mức nợ trung bình'
        }
    )
    
    district1, _ = District.objects.get_or_create(
        district_name='Quận 1',
        defaults={
            'city_name': 'TP.HCM',
            'max_agencies': 10
        }
    )
    
    district2, _ = District.objects.get_or_create(
        district_name='Quận 2',
        defaults={
            'city_name': 'TP.HCM',
            'max_agencies': 15
        }
    )
    
    district3, _ = District.objects.get_or_create(
        district_name='Ba Đình',
        defaults={
            'city_name': 'Hà Nội',
            'max_agencies': 8
        }
    )
    
    # 3. Create Agencies
    print("🏪 Creating agencies...")
    
    agency1, _ = Agency.objects.get_or_create(
        agency_id=1,
        defaults={
            'agency_name': 'Đại lý Kim Long Premium',
            'agency_type': agency_type1,
            'phone_number': '0123456789',
            'address': '123 Đường ABC, Quận 1',
            'district': district1,
            'email': 'kimlong@test.com',
            'representative': 'Nguyễn Văn A',
            'reception_date': '2024-01-15',
            'debt_amount': Decimal('0.00'),
            'user_id': agent_user.user_id
        }
    )
    
    agency2, _ = Agency.objects.get_or_create(
        agency_id=2,
        defaults={
            'agency_name': 'Đại lý Hoàng Gia Corporation',
            'agency_type': agency_type2,
            'phone_number': '0987654321',
            'address': '456 Đường XYZ, Quận 2',
            'district': district2,
            'email': 'hoanggia@test.com',
            'representative': 'Trần Thị B',
            'reception_date': '2024-02-20',
            'debt_amount': Decimal('0.00')
        }
    )
    
    # 4. Create Inventory Units & Items
    print("📦 Creating inventory units and items...")
    
    unit1, _ = Unit.objects.get_or_create(unit_name='Thùng')
    unit2, _ = Unit.objects.get_or_create(unit_name='Chai')
    unit3, _ = Unit.objects.get_or_create(unit_name='Lon')
    unit4, _ = Unit.objects.get_or_create(unit_name='Gói')
    
    item1, _ = Item.objects.get_or_create(
        item_name='Bia Saigon Special thùng 24 chai',
        defaults={
            'unit': unit1,
            'price': Decimal('240000.00'),
            'stock_quantity': 1000,
            'description': 'Bia Saigon Special đóng thùng 24 chai'
        }
    )
    
    item2, _ = Item.objects.get_or_create(
        item_name='Bia Tiger Crystal chai 330ml',
        defaults={
            'unit': unit2,
            'price': Decimal('12000.00'),
            'stock_quantity': 5000,
            'description': 'Bia Tiger Crystal chai thuỷ tinh 330ml'
        }
    )
    
    item3, _ = Item.objects.get_or_create(
        item_name='Bia Heineken lon 330ml',
        defaults={
            'unit': unit3,
            'price': Decimal('15000.00'),
            'stock_quantity': 3000,
            'description': 'Bia Heineken lon nhôm 330ml'
        }
    )
    
    # 5. Create Staff-Agency relationships
    print("👥 Creating staff-agency relationships...")
    
    StaffAgency.objects.get_or_create(
        staff_id=staff_user.user_id,
        agency=agency1
    )
    
    StaffAgency.objects.get_or_create(
        staff_id=staff_user.user_id,
        agency=agency2
    )
    
    # 6. Create Regulations
    print("⚙️ Creating regulations...")
    
    Regulation.objects.get_or_create(
        regulation_key='max_debt_default',
        defaults={
            'regulation_value': '10000000',
            'description': 'Hạn mức nợ mặc định'
        }
    )
    
    Regulation.objects.get_or_create(
        regulation_key='min_stock_alert',
        defaults={
            'regulation_value': '100',
            'description': 'Ngưỡng cảnh báo tồn kho thấp'
        }
    )
    
    Regulation.objects.get_or_create(
        regulation_key='payment_terms_days',
        defaults={
            'regulation_value': '30',
            'description': 'Số ngày thanh toán'
        }
    )
    
    print("✅ Test data creation completed!")
    print("")
    print("📊 SUMMARY:")
    print(f"  • Accounts: {Account.objects.count()}")
    print(f"  • Users: {User.objects.count()}")
    print(f"  • Agency Types: {AgencyType.objects.count()}")
    print(f"  • Districts: {District.objects.count()}")
    print(f"  • Agencies: {Agency.objects.count()}")
    print(f"  • Units: {Unit.objects.count()}")
    print(f"  • Items: {Item.objects.count()}")
    print(f"  • Staff-Agency: {StaffAgency.objects.count()}")
    print(f"  • Regulations: {Regulation.objects.count()}")
    print("")
    print("🎯 Ready for API testing!")

if __name__ == '__main__':
    create_test_data() 