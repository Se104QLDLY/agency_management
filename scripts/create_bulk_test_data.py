#!/usr/bin/env python3
"""
Script tạo dữ liệu test số lượng lớn cho database
Chạy: python create_bulk_test_data.py
"""
import os
import sys
import django
from django.db import transaction
from decimal import Decimal
from datetime import date, datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agency_management.settings')
django.setup()

from authentication.models import Account, User
from agency.models import AgencyType, District, Agency, StaffAgency
from inventory.models import Unit, Item, Receipt, ReceiptDetail, Issue, IssueDetail
from finance.models import Payment, Report
from regulation.models import Regulation

random.seed(42)  # For reproducible data

def create_users_and_accounts():
    """Tạo accounts và users"""
    print("🔑 Creating accounts and users...")
    
    # Admin accounts
    for i in range(3):
        if not Account.objects.filter(username=f'admin{i+1}').exists():
            account = Account.objects.create(
                username=f'admin{i+1}',
                password_hash='pbkdf2_sha256$600000$test$hash',
                account_role='admin'
            )
            User.objects.create(
                account=account,
                full_name=f'Admin User {i+1}',
                email=f'admin{i+1}@company.com',
                phone_number=f'090{i+1}111222',
                address=f'123 Admin Street {i+1}'
            )
    
    # Staff accounts
    for i in range(15):
        if not Account.objects.filter(username=f'staff{i+1}').exists():
            account = Account.objects.create(
                username=f'staff{i+1}',
                password_hash='pbkdf2_sha256$600000$test$hash',
                account_role='staff'
            )
            User.objects.create(
                account=account,
                full_name=f'Staff User {i+1}',
                email=f'staff{i+1}@company.com',
                phone_number=f'091{i+1:02d}333444',
                address=f'456 Staff Avenue {i+1}'
            )
    
    # Agent accounts  
    for i in range(60):
        if not Account.objects.filter(username=f'agent{i+1}').exists():
            account = Account.objects.create(
                username=f'agent{i+1}',
                password_hash='pbkdf2_sha256$600000$test$hash',
                account_role='agent'
            )
            User.objects.create(
                account=account,
                full_name=f'Agent User {i+1}',
                email=f'agent{i+1}@company.com',
                phone_number=f'092{i+1:02d}555666',
                address=f'789 Agent Road {i+1}'
            )
    
    print(f"✅ Created total: {Account.objects.count()} accounts and {User.objects.count()} users")

def create_agency_types():
    """Tạo các loại đại lý"""
    print("🏢 Creating agency types...")
    
    types = [
        ('Loại I', Decimal('100000000')),    # 100M
        ('Loại II', Decimal('50000000')),    # 50M
        ('Cấp A', Decimal('200000000')),     # 200M
        ('Cấp B', Decimal('75000000')),      # 75M
        ('VIP Premium', Decimal('500000000')), # 500M
        ('Thường', Decimal('25000000')),     # 25M
        ('Cao cấp', Decimal('150000000')),   # 150M
    ]
    
    for name, max_debt in types:
        if not AgencyType.objects.filter(type_name=name).exists():
            AgencyType.objects.create(
                type_name=name,
                max_debt=max_debt,
                description=f'Loại đại lý {name} với hạn mức nợ {max_debt:,.0f} VNĐ'
            )
    
    print(f"✅ Created total: {AgencyType.objects.count()} agency types")

def print_summary():
    """In tổng kết dữ liệu đã tạo"""
    print("\n" + "="*60)
    print("📈 DATA CREATION SUMMARY")
    print("="*60)
    print(f"👤 Accounts: {Account.objects.count()}")
    print(f"👥 Users: {User.objects.count()}")
    print(f"🏢 Agency Types: {AgencyType.objects.count()}")
    print("="*60)
    print("✅ BASIC DATA CREATION COMPLETED!")
    print("="*60)

@transaction.atomic
def main():
    """Main function để chạy tất cả"""
    print("🚀 Starting basic test data creation...")
    
    try:
        create_users_and_accounts()
        create_agency_types()
        print_summary()
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    main()
