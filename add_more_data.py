#!/usr/bin/env python3
"""
Script thêm dữ liệu mà không conflict với data có sẵn
Chạy: python add_more_data.py
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

def add_more_items():
    """Thêm nhiều items hơn"""
    print("📦 Adding more items...")
    
    # Thêm items mới
    new_items_data = [
        ('Bánh mì kẹp thịt', 'Cái', 15000, 100),
        ('Phở bò tái', 'Tô', 45000, 50),
        ('Bún chả Hà Nội', 'Suất', 55000, 40),
        ('Cơm tấm sườn', 'Suất', 35000, 80),
        ('Chè ba màu', 'Tô', 18000, 120),
        ('Bánh cuốn Thanh Trì', 'Suất', 25000, 60),
        ('Nem rán Hà Nội', 'Đĩa', 40000, 70),
        ('Bánh xèo miền Tây', 'Cái', 30000, 90),
        ('Hủ tiếu Nam Vang', 'Tô', 38000, 85),
        ('Cao lầu Hội An', 'Tô', 42000, 55),
        ('Mì Quảng', 'Tô', 40000, 65),
        ('Bún bò Huế', 'Tô', 45000, 75),
        ('Chả cá Lã Vọng', 'Suất', 85000, 35),
        ('Bánh chưng', 'Cái', 50000, 40),
        ('Bánh tét', 'Cái', 45000, 50),
        ('Nem chua rán', 'Đĩa', 35000, 60),
        ('Chả lụa', 'Kg', 180000, 30),
        ('Giò thủ', 'Kg', 220000, 25),
        ('Tôm rim', 'Hộp', 65000, 45),
        ('Mắm ruốc', 'Chai', 35000, 80),
    ]
    
    items_added = 0
    for item_name, unit_name, price, stock in new_items_data:
        if not Item.objects.filter(item_name=item_name).exists():
            try:
                unit, created = Unit.objects.get_or_create(unit_name=unit_name)
                Item.objects.create(
                    item_name=item_name,
                    unit=unit,
                    price=Decimal(str(price)),
                    stock_quantity=stock,
                    description=f'Mô tả cho {item_name}'
                )
                items_added += 1
            except Exception as e:
                print(f"⚠️  Error adding {item_name}: {e}")
                continue
    
    print(f"✅ Added {items_added} new items")

def add_more_receipts():
    """Thêm nhiều receipts hơn"""
    print("📋 Adding more receipts...")
    
    agencies = list(Agency.objects.all())
    staff_users = list(User.objects.filter(account__account_role='staff'))
    items = list(Item.objects.all())
    
    if not agencies or not staff_users or not items:
        print("⚠️  Missing required data")
        return
    
    receipts_added = 0
    details_added = 0
    
    # Thêm 50 phiếu nhập mới
    for i in range(50):
        agency = random.choice(agencies)
        user = random.choice(staff_users)
        days_ago = random.randint(1, 90)
        receipt_date = date.today() - timedelta(days=days_ago)
        
        try:
            receipt = Receipt.objects.create(
                receipt_date=receipt_date,
                user_id=user.user_id,
                agency_id=agency.agency_id,
                total_amount=Decimal('0')
            )
            receipts_added += 1
            
            # Thêm 2-4 chi tiết cho mỗi phiếu
            num_items = random.randint(2, 4)
            selected_items = random.sample(items, min(num_items, len(items)))
            
            for item in selected_items:
                quantity = random.randint(10, 100)
                unit_price = item.price
                line_total = quantity * unit_price
                
                ReceiptDetail.objects.create(
                    receipt=receipt,
                    item=item,
                    quantity=quantity,
                    unit_price=unit_price,
                    line_total=line_total
                )
                details_added += 1
                
        except Exception as e:
            print(f"⚠️  Error creating receipt {i}: {e}")
            continue
    
    print(f"✅ Added {receipts_added} receipts and {details_added} details")

def add_more_issues():
    """Thêm nhiều issues hơn"""
    print("📤 Adding more issues...")
    
    agencies = list(Agency.objects.all())
    staff_users = list(User.objects.filter(account__account_role='staff'))
    items = list(Item.objects.filter(stock_quantity__gt=5))
    
    if not agencies or not staff_users or not items:
        print("⚠️  Missing required data")
        return
    
    issues_added = 0
    details_added = 0
    
    # Thêm 80 phiếu xuất mới
    for i in range(80):
        agency = random.choice(agencies)
        user = random.choice(staff_users)
        days_ago = random.randint(1, 90)
        issue_date = date.today() - timedelta(days=days_ago)
        
        try:
            issue = Issue.objects.create(
                issue_date=issue_date,
                agency_id=agency.agency_id,
                user_id=user.user_id,
                total_amount=Decimal('0')
            )
            issues_added += 1
            
            # Thêm 1-3 chi tiết cho mỗi phiếu
            num_items = random.randint(1, 3)
            available_items = [item for item in items if item.stock_quantity > 3]
            if not available_items:
                continue
                
            selected_items = random.sample(available_items, min(num_items, len(available_items)))
            
            for item in selected_items:
                max_quantity = min(item.stock_quantity // 4, 10)
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
                details_added += 1
                
        except Exception as e:
            print(f"⚠️  Error creating issue {i}: {e}")
            continue
    
    print(f"✅ Added {issues_added} issues and {details_added} details")

def add_more_payments():
    """Thêm nhiều payments hơn"""
    print("💰 Adding more payments...")
    
    agencies = list(Agency.objects.filter(debt_amount__gt=1000))
    staff_users = list(User.objects.filter(account__account_role='staff'))
    
    if not agencies or not staff_users:
        print("⚠️  No suitable data found")
        return
    
    payments_added = 0
    
    # Thêm 40 payments mới
    for i in range(40):
        agency = random.choice(agencies)
        user = random.choice(staff_users)
        days_ago = random.randint(1, 90)
        payment_date = date.today() - timedelta(days=days_ago)
        
        # Payment nhỏ để không làm âm debt
        max_payment = min(float(agency.debt_amount) * 0.3, 500000)
        min_payment = 50000
        
        if max_payment > min_payment:
            amount = random.uniform(min_payment, max_payment)
        else:
            amount = min_payment
        
        try:
            Payment.objects.create(
                payment_date=payment_date,
                agency_id=agency.agency_id,
                user_id=user.user_id,
                amount_collected=Decimal(str(round(amount, 2)))
            )
            payments_added += 1
        except Exception as e:
            print(f"⚠️  Error creating payment {i}: {e}")
            continue
    
    print(f"✅ Added {payments_added} payments")

def add_more_reports():
    """Thêm nhiều reports hơn"""
    print("📊 Adding more reports...")
    
    admin_accounts = list(Account.objects.filter(account_role='admin'))
    
    if not admin_accounts:
        print("⚠️  No admin accounts found")
        return
    
    reports_added = 0
    
    # Thêm reports cho 12 tháng qua
    for month_ago in range(12):
        report_date = date.today() - timedelta(days=30 * month_ago)
        
        # Sales report
        sales_data = {
            'total_sales': float(random.uniform(2000000, 8000000)),
            'total_orders': random.randint(80, 300),
            'month': report_date.strftime('%Y-%m'),
            'top_agencies': [
                {'name': f'Agency {i}', 'amount': float(random.uniform(150000, 800000))}
                for i in range(1, 8)
            ],
            'growth_rate': round(random.uniform(-10, 25), 2)
        }
        
        Report.objects.create(
            report_type='sales',
            report_date=report_date,
            data=sales_data,
            created_by=random.choice(admin_accounts)
        )
        reports_added += 1
        
        # Debt report
        debt_data = {
            'total_debt': float(random.uniform(8000000, 30000000)),
            'agencies_in_debt': random.randint(30, 80),
            'overdue_debt': float(random.uniform(2000000, 8000000)),
            'month': report_date.strftime('%Y-%m'),
            'debt_by_type': {
                'Loại 1': float(random.uniform(1000000, 5000000)),
                'Loại 2': float(random.uniform(500000, 3000000)),
                'Cấp 1': float(random.uniform(2000000, 8000000))
            }
        }
        
        Report.objects.create(
            report_type='debt',
            report_date=report_date,
            data=debt_data,
            created_by=random.choice(admin_accounts)
        )
        reports_added += 1
    
    print(f"✅ Added {reports_added} reports")

def print_final_summary():
    """In tổng kết cuối cùng"""
    print("\n" + "="*70)
    print("🎉 FINAL DATABASE SUMMARY")
    print("="*70)
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
    print(f"📊 Reports: {Report.objects.count()}")
    print(f"⚙️ Regulations: {Regulation.objects.count()}")
    print("="*70)
    print("✅ DATABASE IS NOW FULL OF COMPREHENSIVE TEST DATA!")
    print("🚀 READY FOR FRONTEND TESTING!")
    print("="*70)

@transaction.atomic
def main():
    """Main function"""
    print("🚀 Adding MORE test data to existing database...")
    
    try:
        add_more_items()
        add_more_receipts()
        add_more_issues()
        add_more_payments()
        add_more_reports()
        
        print_final_summary()
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    main()
