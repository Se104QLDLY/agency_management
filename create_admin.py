#!/usr/bin/env python
"""
Script to create an admin account for the Agency Management System
"""
import os
import sys
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agency_management.settings")
django.setup()

from authentication.models import Account, User

def create_admin_account():
    """Create an admin account with user profile"""
    print("=== Tạo Account Admin ===")
    
    # Get admin credentials
    username = input("Nhập username cho admin: ").strip()
    if not username:
        print("Username không được để trống!")
        return False
    
    # Check if username already exists
    if Account.objects.filter(username=username).exists():
        print(f"Username '{username}' đã tồn tại!")
        return False
    
    password = input("Nhập password cho admin: ").strip()
    if not password:
        print("Password không được để trống!")
        return False
    
    full_name = input("Nhập họ tên admin: ").strip()
    if not full_name:
        full_name = "Administrator"
    
    email = input("Nhập email admin (tùy chọn): ").strip()
    phone_number = input("Nhập số điện thoại admin (tùy chọn): ").strip()
    address = input("Nhập địa chỉ admin (tùy chọn): ").strip()
    
    try:
        # Create admin account
        admin_account = Account.objects.create_user(
            username=username,
            password=password,
            account_role=Account.ADMIN
        )
        
        # Create user profile
        admin_user = User.objects.create(
            account=admin_account,
            full_name=full_name,
            email=email if email else None,
            phone_number=phone_number if phone_number else None,
            address=address if address else None
        )
        
        print(f"\n✅ Tạo admin account thành công!")
        print(f"Username: {username}")
        print(f"Họ tên: {full_name}")
        print(f"Role: {admin_account.account_role}")
        print(f"Account ID: {admin_account.account_id}")
        print(f"User ID: {admin_user.user_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi tạo admin account: {str(e)}")
        return False

def list_existing_accounts():
    """List all existing accounts"""
    print("\n=== Danh sách Account hiện tại ===")
    accounts = Account.objects.all()
    
    if not accounts:
        print("Không có account nào trong hệ thống.")
        return
    
    for account in accounts:
        user = account.users.first()
        user_name = user.full_name if user else "N/A"
        print(f"- {account.username} ({account.account_role}) - {user_name}")

if __name__ == "__main__":
    print("Agency Management System - Admin Account Creator")
    print("=" * 50)
    
    while True:
        print("\nChọn tùy chọn:")
        print("1. Tạo admin account mới")
        print("2. Xem danh sách account hiện tại")
        print("3. Thoát")
        
        choice = input("\nNhập lựa chọn (1-3): ").strip()
        
        if choice == "1":
            create_admin_account()
        elif choice == "2":
            list_existing_accounts()
        elif choice == "3":
            print("Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ!")
