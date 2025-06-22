#!/usr/bin/env python
"""
Script to create sample data for agency management system
"""
import os
import sys
import django
from datetime import date, datetime, timedelta
from decimal import Decimal

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agency_management.settings')
django.setup()

from agency.models import AgencyType, District, Agency
from authentication.models import User, Account
from inventory.models import Unit, Item, Receipt, Receiptdetail, Issue, Issuedetail
from finance.models import Payment, Report
from regulation.models import Regulation


def create_sample_data():
    print("Creating sample data...")
    
    # 1. Create Agency Types (if not exist)
    agency_types = [
        {"type_name": "Cấp 1", "max_debt": Decimal("100000000.00"), "description": "Đại lý cấp 1 - Hạn mức nợ cao"},
        {"type_name": "Cấp 2", "max_debt": Decimal("50000000.00"), "description": "Đại lý cấp 2 - Hạn mức nợ trung bình"},
        {"type_name": "Cấp 3", "max_debt": Decimal("20000000.00"), "description": "Đại lý cấp 3 - Hạn mức nợ thấp"},
        {"type_name": "VIP", "max_debt": Decimal("200000000.00"), "description": "Đại lý VIP - Hạn mức nợ rất cao"},
    ]
    
    for type_data in agency_types:
        agency_type, created = AgencyType.objects.get_or_create(
            type_name=type_data["type_name"],
            defaults=type_data
        )
        if created:
            print(f"Created agency type: {agency_type.type_name}")
    
    # 2. Create Districts (if not exist)
    districts = [
        {"district_name": "Quận 1", "city_name": "TP.HCM", "max_agencies": 20},
        {"district_name": "Quận 2", "city_name": "TP.HCM", "max_agencies": 15},
        {"district_name": "Quận 3", "city_name": "TP.HCM", "max_agencies": 18},
        {"district_name": "Quận 4", "city_name": "TP.HCM", "max_agencies": 12},
        {"district_name": "Quận 5", "city_name": "TP.HCM", "max_agencies": 25},
        {"district_name": "Quận 6", "city_name": "TP.HCM", "max_agencies": 10},
        {"district_name": "Quận 7", "city_name": "TP.HCM", "max_agencies": 22},
        {"district_name": "Quận 8", "city_name": "TP.HCM", "max_agencies": 14},
        {"district_name": "Quận 9", "city_name": "TP.HCM", "max_agencies": 16},
        {"district_name": "Quận 10", "city_name": "TP.HCM", "max_agencies": 13},
        {"district_name": "Quận 11", "city_name": "TP.HCM", "max_agencies": 19},
        {"district_name": "Quận 12", "city_name": "TP.HCM", "max_agencies": 17},
        {"district_name": "Bình Thạnh", "city_name": "TP.HCM", "max_agencies": 21},
        {"district_name": "Tân Bình", "city_name": "TP.HCM", "max_agencies": 24},
        {"district_name": "Tân Phú", "city_name": "TP.HCM", "max_agencies": 15},
        {"district_name": "Phú Nhuận", "city_name": "TP.HCM", "max_agencies": 8},
        {"district_name": "Gò Vấp", "city_name": "TP.HCM", "max_agencies": 20},
        {"district_name": "Bình Tân", "city_name": "TP.HCM", "max_agencies": 18},
        {"district_name": "Thủ Đức", "city_name": "TP.HCM", "max_agencies": 30},
        {"district_name": "Hóc Môn", "city_name": "TP.HCM", "max_agencies": 12},
    ]
    
    for district_data in districts:
        district, created = District.objects.get_or_create(
            district_name=district_data["district_name"],
            defaults=district_data
        )
        if created:
            print(f"Created district: {district.district_name}")
    
    # 3. Create sample agencies (if not exist)
    agencies_data = [
        {
            "agency_name": "Đại lý Kim Long",
            "phone_number": "0901234567",
            "address": "123 Nguyễn Huệ, Quận 1",
            "email": "kimlong@example.com",
            "representative": "Nguyễn Văn Long",
            "reception_date": date(2024, 1, 15),
            "debt_amount": Decimal("15000000.00"),
            "agency_type": "Cấp 1",
            "district": "Quận 1"
        },
        {
            "agency_name": "Đại lý Hoàng Gia",
            "phone_number": "0902345678", 
            "address": "456 Lê Lợi, Quận 3",
            "email": "hoanggia@example.com",
            "representative": "Trần Thị Hoa",
            "reception_date": date(2024, 2, 20),
            "debt_amount": Decimal("8500000.00"),
            "agency_type": "Cấp 2",
            "district": "Quận 3"
        },
        {
            "agency_name": "Đại lý Thành Đạt",
            "phone_number": "0903456789",
            "address": "789 Hai Bà Trưng, Quận 1", 
            "email": "thanhdat@example.com",
            "representative": "Lê Văn Thành",
            "reception_date": date(2024, 3, 10),
            "debt_amount": Decimal("12000000.00"),
            "agency_type": "Cấp 1",
            "district": "Quận 1"
        }
    ]
    
    for agency_data in agencies_data:
        # Get related objects
        agency_type = AgencyType.objects.get(type_name=agency_data.pop("agency_type"))
        district = District.objects.get(district_name=agency_data.pop("district"))
        
        agency, created = Agency.objects.get_or_create(
            agency_name=agency_data["agency_name"],
            defaults={
                **agency_data,
                "agency_type": agency_type,
                "district": district
            }
        )
        if created:
            print(f"Created agency: {agency.agency_name}")
    
    # 4. Create inventory units
    units_data = [
        {"unit_name": "Cái"},
        {"unit_name": "Thùng"},
        {"unit_name": "Kg"},
        {"unit_name": "Lít"},
        {"unit_name": "Mét"},
        {"unit_name": "Bộ"},
    ]
    
    for unit_data in units_data:
        unit, created = Unit.objects.get_or_create(**unit_data)
        if created:
            print(f"Created unit: {unit.unit_name}")
    
    # 5. Create inventory items
    items_data = [
        {
            "item_name": "Bia Heineken 330ml",
            "unit": "Cái",
            "price": Decimal("25000.00"),
            "stock_quantity": 1000,
            "description": "Bia Heineken lon 330ml"
        },
        {
            "item_name": "Bia Tiger 330ml",
            "unit": "Cái", 
            "price": Decimal("22000.00"),
            "stock_quantity": 1500,
            "description": "Bia Tiger lon 330ml"
        },
        {
            "item_name": "Nước ngọt Coca Cola",
            "unit": "Cái",
            "price": Decimal("15000.00"),
            "stock_quantity": 2000,
            "description": "Nước ngọt Coca Cola lon 330ml"
        },
        {
            "item_name": "Nước suối Aquafina",
            "unit": "Thùng",
            "price": Decimal("120000.00"),
            "stock_quantity": 500,
            "description": "Nước suối Aquafina thùng 24 chai"
        },
        {
            "item_name": "Bánh mì sandwich",
            "unit": "Cái",
            "price": Decimal("35000.00"),
            "stock_quantity": 200,
            "description": "Bánh mì sandwich thập cẩm"
        },
    ]
    
    for item_data in items_data:
        unit = Unit.objects.get(unit_name=item_data.pop("unit"))
        item, created = Item.objects.get_or_create(
            item_name=item_data["item_name"],
            defaults={**item_data, "unit": unit}
        )
        if created:
            print(f"Created item: {item.item_name}")
    
    # 6. Create regulations
    regulations_data = [
        {
            "regulation_key": "max_debt_default",
            "regulation_value": "50000000",
            "description": "Hạn mức nợ mặc định cho đại lý mới (VNĐ)"
        },
        {
            "regulation_key": "min_stock_threshold", 
            "regulation_value": "10",
            "description": "Ngưỡng tồn kho tối thiểu để cảnh báo"
        },
        {
            "regulation_key": "payment_grace_period",
            "regulation_value": "30",
            "description": "Thời gian gia hạn thanh toán (ngày)"
        },
        {
            "regulation_key": "max_agencies_per_district",
            "regulation_value": "25",
            "description": "Số lượng đại lý tối đa trên một quận/huyện"
        },
    ]
    
    for reg_data in regulations_data:
        regulation, created = Regulation.objects.get_or_create(
            regulation_key=reg_data["regulation_key"],
            defaults=reg_data
        )
        if created:
            print(f"Created regulation: {regulation.regulation_key}")
    
    # 7. Create sample receipts and issues (if we have users)
    try:
        user = User.objects.first()
        agency = Agency.objects.first()
        
        if user and agency:
            # Create sample receipt
            receipt, created = Receipt.objects.get_or_create(
                receipt_id=1,
                defaults={
                    "receipt_date": date.today() - timedelta(days=5),
                    "user_id": user.user_id,
                    "agency_id": agency.agency_id,
                    "total_amount": Decimal("0.00")
                }
            )
            if created:
                print(f"Created sample receipt: {receipt.receipt_id}")
                
                # Add receipt details
                item = Item.objects.first()
                if item:
                    detail, detail_created = Receiptdetail.objects.get_or_create(
                        receipt=receipt,
                        item=item,
                        defaults={
                            "quantity": 100,
                            "unit_price": item.price,
                            "line_total": 100 * item.price
                        }
                    )
                    if detail_created:
                        print(f"Created receipt detail for item: {item.item_name}")
            
            # Create sample payment
            payment, created = Payment.objects.get_or_create(
                payment_id=1,
                defaults={
                    "payment_date": date.today() - timedelta(days=2),
                    "agency_id": agency.agency_id,
                    "user_id": user.user_id,
                    "amount_collected": Decimal("5000000.00")
                }
            )
            if created:
                print(f"Created sample payment: {payment.payment_id}")
    
    except Exception as e:
        print(f"Could not create sample transactions: {e}")
    
    # 4. Create inventory units
    units_data = [
        {"unit_name": "Cái"},
        {"unit_name": "Thùng"},
        {"unit_name": "Kg"},
        {"unit_name": "Lít"},
        {"unit_name": "Mét"},
        {"unit_name": "Bộ"},
    ]
    
    for unit_data in units_data:
        unit, created = Unit.objects.get_or_create(**unit_data)
        if created:
            print(f"Created unit: {unit.unit_name}")
    
    # 5. Create inventory items
    items_data = [
        {
            "item_name": "Bia Heineken 330ml",
            "unit": "Cái",
            "price": Decimal("25000.00"),
            "stock_quantity": 1000,
            "description": "Bia Heineken lon 330ml"
        },
        {
            "item_name": "Bia Tiger 330ml",
            "unit": "Cái", 
            "price": Decimal("22000.00"),
            "stock_quantity": 1500,
            "description": "Bia Tiger lon 330ml"
        },
        {
            "item_name": "Nước ngọt Coca Cola",
            "unit": "Cái",
            "price": Decimal("15000.00"),
            "stock_quantity": 2000,
            "description": "Nước ngọt Coca Cola lon 330ml"
        },
        {
            "item_name": "Nước suối Aquafina",
            "unit": "Thùng",
            "price": Decimal("120000.00"),
            "stock_quantity": 500,
            "description": "Nước suối Aquafina thùng 24 chai"
        },
        {
            "item_name": "Bánh mì sandwich",
            "unit": "Cái",
            "price": Decimal("35000.00"),
            "stock_quantity": 200,
            "description": "Bánh mì sandwich thập cẩm"
        },
    ]
    
    for item_data in items_data:
        unit = Unit.objects.get(unit_name=item_data.pop("unit"))
        item, created = Item.objects.get_or_create(
            item_name=item_data["item_name"],
            defaults={**item_data, "unit": unit}
        )
        if created:
            print(f"Created item: {item.item_name}")
    
    # 6. Create regulations
    regulations_data = [
        {
            "regulation_key": "max_debt_default",
            "regulation_value": "50000000",
            "description": "Hạn mức nợ mặc định cho đại lý mới (VNĐ)"
        },
        {
            "regulation_key": "min_stock_threshold", 
            "regulation_value": "10",
            "description": "Ngưỡng tồn kho tối thiểu để cảnh báo"
        },
        {
            "regulation_key": "payment_grace_period",
            "regulation_value": "30",
            "description": "Thời gian gia hạn thanh toán (ngày)"
        },
        {
            "regulation_key": "max_agencies_per_district",
            "regulation_value": "25",
            "description": "Số lượng đại lý tối đa trên một quận/huyện"
        },
    ]
    
    for reg_data in regulations_data:
        regulation, created = Regulation.objects.get_or_create(
            regulation_key=reg_data["regulation_key"],
            defaults=reg_data
        )
        if created:
            print(f"Created regulation: {regulation.regulation_key}")
    
    # 7. Create sample receipts and issues (if we have users)
    try:
        user = User.objects.first()
        agency = Agency.objects.first()
        
        if user and agency:
            # Create sample receipt
            receipt, created = Receipt.objects.get_or_create(
                receipt_id=1,
                defaults={
                    "receipt_date": date.today() - timedelta(days=5),
                    "user_id": user.user_id,
                    "agency_id": agency.agency_id,
                    "total_amount": Decimal("0.00")
                }
            )
            if created:
                print(f"Created sample receipt: {receipt.receipt_id}")
                
                # Add receipt details
                item = Item.objects.first()
                if item:
                    detail, detail_created = Receiptdetail.objects.get_or_create(
                        receipt=receipt,
                        item=item,
                        defaults={
                            "quantity": 100,
                            "unit_price": item.price,
                            "line_total": 100 * item.price
                        }
                    )
                    if detail_created:
                        print(f"Created receipt detail for item: {item.item_name}")
            
            # Create sample payment
            payment, created = Payment.objects.get_or_create(
                payment_id=1,
                defaults={
                    "payment_date": date.today() - timedelta(days=2),
                    "agency_id": agency.agency_id,
                    "user_id": user.user_id,
                    "amount_collected": Decimal("5000000.00")
                }
            )
            if created:
                print(f"Created sample payment: {payment.payment_id}")
    
    except Exception as e:
        print(f"Could not create sample transactions: {e}")
    
    print("Sample data creation completed!")


if __name__ == "__main__":
    create_sample_data() 