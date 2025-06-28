#!/usr/bin/env python3
"""
Script tạo dữ liệu test ĐẦY ĐỦ cho database
Chạy: python create_full_test_data.py
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

def create_districts():
    """Tạo các quận/huyện"""
    print("🏘️ Creating districts...")
    
    districts = [
        ('TP. Hồ Chí Minh', 'Quận 1', 20),
        ('TP. Hồ Chí Minh', 'Quận 2', 18),
        ('TP. Hồ Chí Minh', 'Quận 3', 15),
        ('TP. Hồ Chí Minh', 'Quận 4', 12),
        ('TP. Hồ Chí Minh', 'Quận 5', 25),
        ('TP. Hồ Chí Minh', 'Quận 6', 22),
        ('TP. Hồ Chí Minh', 'Quận 7', 30),
        ('TP. Hồ Chí Minh', 'Quận 8', 18),
        ('TP. Hồ Chí Minh', 'Quận 9', 35),
        ('TP. Hồ Chí Minh', 'Quận 10', 16),
        ('TP. Hồ Chí Minh', 'Quận 11', 20),
        ('TP. Hồ Chí Minh', 'Quận 12', 28),
        ('TP. Hồ Chí Minh', 'Quận Bình Thạnh', 32),
        ('TP. Hồ Chí Minh', 'Quận Gò Vấp', 40),
        ('TP. Hồ Chí Minh', 'Quận Phú Nhuận', 18),
        ('TP. Hồ Chí Minh', 'Quận Tân Bình', 45),
        ('TP. Hồ Chí Minh', 'Quận Tân Phú', 35),
        ('Hà Nội', 'Quận Ba Đình', 25),
        ('Hà Nội', 'Quận Hoàn Kiếm', 15),
        ('Hà Nội', 'Quận Hai Bà Trưng', 30),
        ('Hà Nội', 'Quận Đống Đa', 35),
        ('Hà Nội', 'Quận Cầu Giấy', 28),
        ('Đà Nẵng', 'Quận Hải Châu', 22),
        ('Đà Nẵng', 'Quận Sơn Trà', 25),
        ('Cần Thơ', 'Quận Ninh Kiều', 20),
        ('Cần Thơ', 'Quận Bình Thủy', 18),
    ]
    
    for city, district, max_agencies in districts:
        if not District.objects.filter(district_name=district).exists():
            District.objects.create(
                city_name=city,
                district_name=district,
                max_agencies=max_agencies
            )
    
    print(f"✅ Created total: {District.objects.count()} districts")

def create_agencies():
    """Tạo các đại lý"""
    print("🏪 Creating agencies...")
    
    agency_types = list(AgencyType.objects.all())
    districts = list(District.objects.all()) 
    agent_users = list(User.objects.filter(account__account_role='agent', agency__isnull=True))
    
    company_names = [
        'Thành Đạt', 'Hòa Bình', 'Thịnh Vượng', 'Kim Ngân', 'Phát Tài',
        'Minh Châu', 'Đông Dương', 'Việt Nam', 'Sài Gòn', 'Hà Nội',
        'Mekong', 'Đồng Nai', 'Bình Dương', 'Long An', 'Tiền Giang',
        'An Giang', 'Cần Thơ', 'Kiên Giang', 'Đồng Tháp', 'Vĩnh Long'
    ]
    
    # Tạo 50 đại lý mới
    agencies_created = 0
    current_count = Agency.objects.count()
    
    for i in range(50):
        if current_count + agencies_created >= 150:
            break
            
        agency_type = random.choice(agency_types)
        district = random.choice(districts)
        
        # Random debt từ 0 đến 70% max_debt
        max_debt = agency_type.max_debt
        current_debt = random.uniform(0, float(max_debt) * 0.7)
        
        reception_date = date.today() - timedelta(days=random.randint(30, 730))
        company_name = random.choice(company_names)
        
        # Tạo agency
        agency = Agency.objects.create(
            agency_name=f'Đại lý {company_name} {district.district_name} #{current_count + agencies_created + 1}',
            agency_type=agency_type,
            phone_number=f'028{random.randint(10000000, 99999999)}',
            address=f'Số {random.randint(1, 999)} đường {random.choice(["Nguyễn Trãi", "Lê Lợi", "Hai Bà Trưng", "Trần Hưng Đạo", "Võ Thị Sáu"])}, {district.district_name}',
            district=district,
            email=f'agency{current_count + agencies_created + 1}@{company_name.lower().replace(" ", "")}.com',
            representative=f'Ông/Bà {random.choice(["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng"])} Văn {chr(65 + (agencies_created % 26))}',
            reception_date=reception_date,
            debt_amount=Decimal(str(round(current_debt, 2))),
        )
        
        # Gán agent user nếu có
        if agent_users:
            agent_user = agent_users.pop(0)
            agency.user = agent_user
            agency.save()
        
        agencies_created += 1
    
    print(f"✅ Created {agencies_created} new agencies, total: {Agency.objects.count()}")

def print_summary():
    """In tổng kết dữ liệu đã tạo"""
    print("\n" + "="*60)
    print("📈 FULL DATA CREATION SUMMARY")
    print("="*60)
    print(f"👤 Accounts: {Account.objects.count()}")
    print(f"👥 Users: {User.objects.count()}")
    print(f"🏢 Agency Types: {AgencyType.objects.count()}")
    print(f"🏘️ Districts: {District.objects.count()}")
    print(f"🏪 Agencies: {Agency.objects.count()}")
    print("="*60)
    print("✅ AGENCIES AND DISTRICTS CREATION COMPLETED!")
    print("="*60)

@transaction.atomic
def main():
    """Main function để chạy tất cả"""
    print("🚀 Starting agencies and districts creation...")
    
    try:
        create_districts()
        create_agencies()
        print_summary()
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    main()
