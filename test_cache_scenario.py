#!/usr/bin/env python3
"""
Script để test cache issue - tạo test scenario cho user Tuu và Thắng
"""
import os
import sys
import django

# Add the Django project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agency_management.settings')
django.setup()

from authentication.models import User, Account
from agency.models import Agency
from django.contrib.auth.hashers import make_password

def test_cache_scenario():
    """Test scenario cho cache issue"""
    print("=== TESTING CACHE ISSUE SCENARIO ===")
    
    # Tìm user Tuu
    try:
        tuu_account = Account.objects.get(username='Tuu')
        tuu_user = User.objects.get(account=tuu_account)
        print(f"✓ Found Tuu: ID={tuu_user.user_id}, Role={tuu_user.account.account_role}")
        
        # Kiểm tra agency của Tuu
        try:
            tuu_agency = Agency.objects.get(user_id=tuu_user.user_id)
            print(f"  ⚠️  Tuu có agency: {tuu_agency.agency_name} (ID: {tuu_agency.agency_id})")
        except Agency.DoesNotExist:
            print(f"  ✓ Tuu KHÔNG có agency - đúng như mong đợi")
    except Account.DoesNotExist:
        print("✗ Không tìm thấy user Tuu")
        return
    
    # Tìm user Thắng
    try:
        thang_account = Account.objects.get(username='Thang')
        thang_user = User.objects.get(account=thang_account)
        print(f"✓ Found Thắng: ID={thang_user.user_id}, Role={thang_user.account.account_role}")
        
        # Kiểm tra agency của Thắng
        try:
            thang_agency = Agency.objects.get(user_id=thang_user.user_id)
            print(f"  ✓ Thắng có agency: {thang_agency.agency_name} (ID: {thang_agency.agency_id})")
        except Agency.DoesNotExist:
            print(f"  ⚠️  Thắng KHÔNG có agency")
    except Account.DoesNotExist:
        print("✗ Không tìm thấy user Thắng")
        return
    
    print("\n=== CACHE ISSUE ANALYSIS ===")
    print("Vấn đề: User Tuu (không có agency) nhưng hiển thị thông tin agency của Thắng")
    print("Nguyên nhân có thể:")
    print("1. Browser cache đang lưu dữ liệu cũ")
    print("2. JWT token chưa được refresh đúng")
    print("3. Frontend state không được clear khi user thay đổi")
    print("4. API response bị cache")
    
    print("\n=== SUGGESTED TESTING STEPS ===")
    print("1. Mở Developer Tools (F12)")
    print("2. Clear tất cả cache và cookies:")
    print("   - Application tab > Storage > Clear all")
    print("   - Network tab > Disable cache checkbox")
    print("3. Đăng nhập user Tuu")
    print("4. Kiểm tra network requests:")
    print(f"   - GET /api/v1/auth/me/ should return user_id={tuu_user.user_id}, agency_id=null")
    print("   - Không được có requests tới /api/v1/agency/{id}/")
    print("5. Kiểm tra console logs xem có thông tin user nào")

def create_clean_test_users():
    """Tạo test users sạch để test"""
    print("\n=== CREATING CLEAN TEST USERS ===")
    
    # Tạo test agent không có agency
    try:
        test_agent_account, created = Account.objects.get_or_create(
            username='test_clean_agent',
            defaults={
                'password_hash': make_password('Test123!'),
                'account_role': 'agent'
            }
        )
        if created:
            test_agent_user = User.objects.create(
                account=test_agent_account,
                full_name='Test Clean Agent',
                email='test_clean_agent@test.com',
                phone_number='0900000001',
                address='Test Address'
            )
            print(f"✓ Created clean test agent: {test_agent_user.full_name} (ID: {test_agent_user.user_id})")
        else:
            test_agent_user = User.objects.get(account=test_agent_account)
            print(f"✓ Test agent already exists: {test_agent_user.full_name} (ID: {test_agent_user.user_id})")
    except Exception as e:
        print(f"✗ Error creating test agent: {e}")
        return
    
    # Kiểm tra rằng test agent không có agency
    try:
        test_agency = Agency.objects.get(user_id=test_agent_user.user_id)
        print(f"  ⚠️  WARNING: Test agent có agency: {test_agency.agency_name}")
    except Agency.DoesNotExist:
        print(f"  ✓ Test agent không có agency - perfect!")
    
    print(f"\n=== TEST LOGIN CREDENTIALS ===")
    print(f"Username: test_clean_agent")
    print(f"Password: Test123!")
    print(f"Expected behavior: Thấy thông báo 'Chưa Được Phân Công Đại Lý'")

if __name__ == '__main__':
    test_cache_scenario()
    create_clean_test_users()
