#!/usr/bin/env python
"""
Simple script to create an admin account quickly
"""
import os
import sys
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agency_management.settings")
django.setup()

from authentication.models import Account, User

def create_admin_quickly():
    """Create admin account quickly with predefined values"""
    
    # Predefined admin values
    username = "admin"
    password = "admin123"
    full_name = "Administrator"
    email = "admin@example.com"
    
    try:
        # Check if admin already exists
        if Account.objects.filter(username=username).exists():
            print(f"❌ Admin account '{username}' đã tồn tại!")
            return False
        
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
            email=email,
            phone_number="0123456789",
            address="Hệ thống quản lý"
        )
        
        print(f"✅ Tạo admin account thành công!")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Họ tên: {full_name}")
        print(f"Email: {email}")
        print(f"Role: {admin_account.account_role}")
        print(f"Account ID: {admin_account.account_id}")
        print(f"User ID: {admin_user.user_id}")
        print(f"\n🔐 Bạn có thể đăng nhập với:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi tạo admin account: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Tạo Admin Account Nhanh")
    print("=" * 40)
    create_admin_quickly()
