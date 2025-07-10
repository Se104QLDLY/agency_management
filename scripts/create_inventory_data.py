#!/usr/bin/env python3
"""
Script tạo dữ liệu inventory và finance  
Chạy: python create_inventory_data.py
"""
import os
import sys
import django
from django.db import transaction
from decimal import Decimal
from datetime import date, datetime, timedelta
import random
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agency_management.settings')
django.setup()

from authentication.models import Account, User
from agency.models import AgencyType, District, Agency, StaffAgency
from inventory.models import Unit, Item, Receipt, ReceiptDetail, Issue, IssueDetail
from finance.models import Payment, Report
from regulation.models import Regulation

random.seed(42)  # For reproducible data

def create_units_and_items():
    """Tạo đơn vị và sản phẩm"""
    print("📦 Creating units and items...")
    
    # Units
    units_data = ['Cái', 'Hộp', 'Thùng', 'Kg', 'Lít', 'Gói', 'Chai', 'Túi', 'Bộ', 'Chiếc', 'Tá', 'Chục']
    for unit_name in units_data:
        if not Unit.objects.filter(unit_name=unit_name).exists():
            Unit.objects.create(unit_name=unit_name)
    
    # Items  
    items_data = [
        ('Sữa tươi Vinamilk 1L', 'Hộp', 25000, 150),
        ('Bánh mì sandwich', 'Cái', 8000, 200),
        ('Nước ngọt Coca Cola 330ml', 'Chai', 12000, 300),
        ('Bia Heineken 330ml', 'Chai', 22000, 180),
        ('Cà phê G7 3in1', 'Hộp', 45000, 120),
        ('Trà xanh 0 độ 450ml', 'Chai', 15000, 250),
        ('Nước suối Lavie 500ml', 'Chai', 5000, 500),
        ('Bánh quy Oreo', 'Gói', 18000, 180),
        ('Kẹo Alpenliebe', 'Gói', 25000, 150),
        ('Chocolate Kitkat', 'Cái', 12000, 200),
        ('Mì tôm Hảo Hảo', 'Gói', 4000, 800),
        ('Cơm hộp Kinh Đô', 'Hộp', 35000, 100),
        ('Xúc xích CP 500g', 'Gói', 55000, 80),
        ('Chả cá Thanh Hóa', 'Kg', 180000, 50),
        ('Tôm khô Cà Mau', 'Kg', 350000, 30),
        ('Mắm tôm Tây Ninh', 'Chai', 45000, 70),
        ('Gạo ST25 Đồng Tháp', 'Kg', 35000, 200),
        ('Đường trắng Biên Hòa', 'Kg', 22000, 300),
        ('Muối i-ốt Việt Nam', 'Gói', 8000, 150),
        ('Dầu ăn Neptune 1L', 'Chai', 65000, 120),
        ('Tương ớt Cholimex', 'Chai', 28000, 100),
        ('Nước mắm Nam Ngư', 'Chai', 45000, 90),
        ('Bánh tráng Tây Ninh', 'Gói', 15000, 200),
        ('Chao Hà Nội', 'Hộp', 25000, 80),
        ('Dưa chua Đà Lạt', 'Gói', 20000, 100),
        ('Rau muống sạch', 'Kg', 12000, 50),
        ('Cà chua Đà Lạt', 'Kg', 25000, 80),
        ('Khoai tây Đà Lạt', 'Kg', 30000, 100),
        ('Hành tây Vinh', 'Kg', 18000, 120),
        ('Tỏi Lý Sơn', 'Kg', 85000, 60),
        ('Ớt hiểm Nghệ An', 'Kg', 120000, 40),
        ('Thịt heo sạch CP', 'Kg', 180000, 100),
        ('Thịt bò Úc', 'Kg', 350000, 50),
        ('Gà ta Kiến Giang', 'Kg', 120000, 80),
        ('Cá tra Vĩnh Long', 'Kg', 65000, 90),
        ('Tôm sú Cà Mau', 'Kg', 450000, 40),
        ('Cua biển Kiên Giang', 'Kg', 280000, 30),
        ('Sữa chua Vinamilk', 'Hộp', 8000, 300),
        ('Yaourt Kun', 'Hộp', 6000, 250),
        ('Kem Merino', 'Cái', 15000, 180),
        ('Bánh bao CJ', 'Cái', 12000, 150),
        ('Nem chua Thanh Hóa', 'Gói', 35000, 70),
        ('Chả lụa Hà Nội', 'Kg', 150000, 60),
        ('Giò thủ Nam Định', 'Kg', 180000, 40),
        ('Bánh chưng Hưng Yên', 'Cái', 45000, 100),
        ('Bánh tét Trà Vinh', 'Cái', 40000, 80),
        ('Rượu vang Đà Lạt', 'Chai', 185000, 50),
        ('Bia Sài Gòn 330ml', 'Chai', 18000, 200),
        ('Vodka Hanoi', 'Chai', 250000, 30),
        ('Whisky Chivas', 'Chai', 850000, 20),
    ]
    
    items_created = 0
    for item_name, unit_name, price, stock in items_data:
        if not Item.objects.filter(item_name=item_name).exists():
            try:
                unit = Unit.objects.get(unit_name=unit_name)
                Item.objects.create(
                    item_name=item_name,
                    unit=unit,
                    price=Decimal(str(price)),
                    stock_quantity=stock,
                    description=f'Mô tả cho {item_name}'
                )
                items_created += 1
            except Unit.DoesNotExist:
                print(f"⚠️  Unit {unit_name} not found for {item_name}")
                continue
    
    print(f"✅ Created {items_created} new items, total: {Item.objects.count()} items and {Unit.objects.count()} units")

def create_receipts_and_details():
    """Tạo phiếu nhập và chi tiết"""
    print("📋 Creating receipts and details...")
    
    agencies = list(Agency.objects.all())
    staff_users = list(User.objects.filter(account__account_role='staff'))
    items = list(Item.objects.all())
    
    if not agencies or not staff_users or not items:
        print("⚠️  Missing required data for receipts")
        return
    
    receipts_created = 0
    details_created = 0
    
    # Tạo 100 phiếu nhập trong 2 tháng qua
    for i in range(100):
        agency = random.choice(agencies)
        user = random.choice(staff_users)
        days_ago = random.randint(1, 60)
        receipt_date = date.today() - timedelta(days=days_ago)
        
        receipt = Receipt.objects.create(
            receipt_date=receipt_date,
            user=user,
            agency=agency,
            total_amount=Decimal('0')  # Sẽ được trigger tính toán
        )
        receipts_created += 1
        
        # Tạo chi tiết cho mỗi phiếu (2-5 sản phẩm)
        num_items = random.randint(2, 5)
        selected_items = random.sample(items, min(num_items, len(items)))
        
        for item in selected_items:
            quantity = random.randint(5, 50)
            unit_price = item.price
            line_total = quantity * unit_price
            
            ReceiptDetail.objects.create(
                receipt=receipt,
                item=item,
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total
            )
            details_created += 1
    
    print(f"✅ Created {receipts_created} receipts and {details_created} receipt details")

def create_issues_and_details():
    """Tạo phiếu xuất và chi tiết"""
    print("📤 Creating issues and details...")
    
    agencies = list(Agency.objects.all())
    staff_users = list(User.objects.filter(account__account_role='staff'))
    items = list(Item.objects.filter(stock_quantity__gt=10))  # Chỉ lấy item có stock > 10
    
    if not agencies or not staff_users or not items:
        print("⚠️  Missing required data for issues")
        return
    
    issues_created = 0
    details_created = 0
    
    # Tạo 150 phiếu xuất trong 2 tháng qua
    for i in range(150):
        agency = random.choice(agencies)
        user = random.choice(staff_users)
        days_ago = random.randint(1, 60)
        issue_date = date.today() - timedelta(days=days_ago)
        
        try:
            issue = Issue.objects.create(
                issue_date=issue_date,
                agency=agency,
                user=user,
                total_amount=Decimal('0')  # Sẽ được trigger tính toán
            )
            issues_created += 1
            
            # Tạo chi tiết cho mỗi phiếu (1-3 sản phẩm)
            num_items = random.randint(1, 3)
            available_items = [item for item in items if item.stock_quantity > 5]
            if not available_items:
                continue
                
            selected_items = random.sample(available_items, min(num_items, len(available_items)))
            
            for item in selected_items:
                max_quantity = min(item.stock_quantity // 3, 15)  # Không xuất quá 1/3 stock hoặc 15
                if max_quantity <= 0:
                    continue
                    
                quantity = random.randint(1, max_quantity)
                unit_price = item.price
                line_total = quantity * unit_price
                
                IssueDetail.objects.create(
                    issue=issue,
                    item=item,
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=line_total
                )
                details_created += 1
        except Exception as e:
            print(f"⚠️  Error creating issue {i}: {e}")
            continue
    
    print(f"✅ Created {issues_created} issues and {details_created} issue details")

def create_payments():
    """Tạo thanh toán"""
    print("💰 Creating payments...")
    
    agencies = list(Agency.objects.filter(debt_amount__gt=0))  # Chỉ agency có nợ
    staff_users = list(User.objects.filter(account__account_role='staff'))
    
    if not agencies or not staff_users:
        print("⚠️  No agencies with debt or staff users found")
        return
    
    payments_created = 0
    
    # Tạo 60 thanh toán trong 2 tháng qua
    for i in range(60):
        if not agencies:
            break
            
        agency = random.choice(agencies)
        user = random.choice(staff_users)
        days_ago = random.randint(1, 60)
        payment_date = date.today() - timedelta(days=days_ago)
        
        # Thanh toán từ 10% đến 40% nợ hiện tại
        max_payment = float(agency.debt_amount) * 0.4
        min_payment = min(100000, float(agency.debt_amount) * 0.1)
        
        if max_payment > min_payment:
            amount = random.uniform(min_payment, max_payment)
        else:
            amount = min_payment
        
        try:
            Payment.objects.create(
                payment_date=payment_date,
                agency=agency,
                user=user,
                amount_collected=Decimal(str(round(amount, 2)))
            )
            payments_created += 1
        except Exception as e:
            print(f"⚠️  Error creating payment {i}: {e}")
            continue
    
    print(f"✅ Created {payments_created} payments")

def create_regulations():
    """Tạo quy định hệ thống"""
    print("⚙️ Creating regulations...")
    
    admin_user = User.objects.filter(account__account_role='admin').first()
    
    if not admin_user:
        print("⚠️  No admin user found")
        return
    
    regulations_data = [
        ('MAX_DEBT_LIMIT', '50000000', 'Hạn mức nợ tối đa mặc định'),
        ('MAX_AGENCIES_PER_DISTRICT', '50', 'Số lượng đại lý tối đa mỗi quận'),
        ('MIN_STOCK_ALERT', '10', 'Cảnh báo khi stock dưới mức này'),
        ('PAYMENT_TERMS_DAYS', '30', 'Số ngày thanh toán'),
        ('AUTO_BACKUP_ENABLED', 'true', 'Tự động backup database'),
        ('NOTIFICATION_EMAIL', 'admin@company.com', 'Email nhận thông báo'),
        ('CURRENCY', 'VND', 'Đơn vị tiền tệ'),
        ('BUSINESS_HOURS', '08:00-17:00', 'Giờ làm việc'),
        ('MAINTENANCE_MODE', 'false', 'Chế độ bảo trì'),
        ('API_RATE_LIMIT', '1000', 'Giới hạn API calls/hour'),
    ]
    
    regulations_created = 0
    for key, value, desc in regulations_data:
        if not Regulation.objects.filter(regulation_key=key).exists():
            Regulation.objects.create(
                regulation_key=key,
                regulation_value=value,
                description=desc,
                last_updated_by=admin_user,
                updated_at=timezone.now()
            )
            regulations_created += 1
    
    print(f"✅ Created {regulations_created} new regulations, total: {Regulation.objects.count()}")

def print_summary():
    """In tổng kết dữ liệu đã tạo"""
    print("\n" + "="*60)
    print("📈 INVENTORY & FINANCE DATA SUMMARY")
    print("="*60)
    print(f"👤 Accounts: {Account.objects.count()}")
    print(f"👥 Users: {User.objects.count()}")
    print(f"🏢 Agency Types: {AgencyType.objects.count()}")
    print(f"🏘️ Districts: {District.objects.count()}")
    print(f"🏪 Agencies: {Agency.objects.count()}")
    print(f"📏 Units: {Unit.objects.count()}")
    print(f"📦 Items: {Item.objects.count()}")
    print(f"📋 Receipts: {Receipt.objects.count()}")
    print(f"📋 Receipt Details: {ReceiptDetail.objects.count()}")
    print(f"📤 Issues: {Issue.objects.count()}")
    print(f"📤 Issue Details: {IssueDetail.objects.count()}")
    print(f"💰 Payments: {Payment.objects.count()}")
    print(f"⚙️ Regulations: {Regulation.objects.count()}")
    print("="*60)
    print("✅ INVENTORY & FINANCE DATA CREATION COMPLETED!")
    print("="*60)

@transaction.atomic
def main():
    """Main function để chạy tất cả"""
    print("�� Starting inventory & finance data creation...")
    
    try:
        create_units_and_items()
        create_receipts_and_details()
        create_issues_and_details()
        create_payments()
        create_regulations()
        
        print_summary()
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    main()
