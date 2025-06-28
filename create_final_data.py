#!/usr/bin/env python3
"""
Script tạo dữ liệu cuối cùng với đúng field names
Chạy: python create_final_data.py
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
            user_id=user.user_id,  # Sử dụng user_id
            agency_id=agency.agency_id,  # Sử dụng agency_id
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
                agency_id=agency.agency_id,  # Sử dụng agency_id
                user_id=user.user_id,  # Sử dụng user_id
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
                agency_id=agency.agency_id,  # Sử dụng agency_id
                user_id=user.user_id,  # Sử dụng user_id
                amount_collected=Decimal(str(round(amount, 2)))
            )
            payments_created += 1
        except Exception as e:
            print(f"⚠️  Error creating payment {i}: {e}")
            continue
    
    print(f"✅ Created {payments_created} payments")

def create_reports():
    """Tạo báo cáo"""
    print("📊 Creating reports...")
    
    admin_accounts = list(Account.objects.filter(account_role='admin'))
    
    if not admin_accounts:
        print("⚠️  No admin accounts found")
        return
    
    reports_created = 0
    
    # Tạo báo cáo hàng tháng trong 6 tháng qua
    for month_ago in range(6):
        report_date = date.today() - timedelta(days=30 * month_ago)
        
        # Sales report
        sales_data = {
            'total_sales': float(random.uniform(1000000, 5000000)),
            'total_orders': random.randint(50, 200),
            'month': report_date.strftime('%Y-%m'),
            'top_agencies': [
                {'name': f'Agency {i}', 'amount': float(random.uniform(100000, 500000))}
                for i in range(1, 6)
            ]
        }
        
        Report.objects.create(
            report_type='sales',
            report_date=report_date,
            data=sales_data,
            created_by=random.choice(admin_accounts)
        )
        reports_created += 1
        
        # Debt report
        debt_data = {
            'total_debt': float(random.uniform(5000000, 20000000)),
            'agencies_in_debt': random.randint(20, 50),
            'overdue_debt': float(random.uniform(1000000, 5000000)),
            'month': report_date.strftime('%Y-%m')
        }
        
        Report.objects.create(
            report_type='debt',
            report_date=report_date,
            data=debt_data,
            created_by=random.choice(admin_accounts)
        )
        reports_created += 1
    
    print(f"✅ Created {reports_created} reports")

def print_summary():
    """In tổng kết dữ liệu đã tạo"""
    print("\n" + "="*60)
    print("📈 FINAL DATA CREATION SUMMARY")
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
    print(f"�� Reports: {Report.objects.count()}")
    print(f"⚙️ Regulations: {Regulation.objects.count()}")
    print("="*60)
    print("✅ ALL DATA CREATION COMPLETED!")
    print("🎉 DATABASE IS NOW FULL OF TEST DATA!")
    print("="*60)

@transaction.atomic
def main():
    """Main function để chạy tất cả"""
    print("🚀 Starting final data creation with correct field names...")
    
    try:
        create_receipts_and_details()
        create_issues_and_details()
        create_payments()
        create_reports()
        
        print_summary()
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    main()
