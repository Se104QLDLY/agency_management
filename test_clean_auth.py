#!/usr/bin/env python3
"""
Script to clear all cache and test clean authentication
"""
import os
import sys
import django

# Add the Django project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agency_management.settings')
django.setup()

from django.core.management import call_command
from authentication.models import User, Account
from agency.models import Agency

def force_clear_django_cache():
    """Clear all Django cache"""
    print("=== CLEARING DJANGO CACHE ===")
    try:
        call_command('clear_cache')
        print("✓ Django cache cleared")
    except:
        print("! Django cache clear failed or not available")

def test_api_responses():
    """Test API responses for problematic users"""
    print("\n=== TESTING API RESPONSES ===")
    
    # Test Tuu (should have no agency)
    try:
        tuu = User.objects.select_related('account').get(user_id=13)
        print(f"Tuu (ID: 13): {tuu.full_name}")
        print(f"  Username: {tuu.account.username}")
        print(f"  Role: {tuu.account.account_role}")
        print(f"  Email: {tuu.email}")
        
        # Check if Tuu has agency
        try:
            agency = Agency.objects.get(user_id=13)
            print(f"  ❌ ERROR: Tuu SHOULD NOT have agency but found: {agency.agency_name}")
        except Agency.DoesNotExist:
            print(f"  ✓ Correct: Tuu has no agency")
            
    except User.DoesNotExist:
        print("❌ Tuu not found")
    
    # Test Thắng (should have agency)
    try:
        thang = User.objects.select_related('account').get(user_id=4)
        print(f"\nThắng (ID: 4): {thang.full_name}")
        print(f"  Username: {thang.account.username}")
        print(f"  Role: {thang.account.account_role}")
        print(f"  Email: {thang.email}")
        
        # Check if Thắng has agency
        try:
            agency = Agency.objects.get(user_id=4)
            print(f"  ✓ Correct: Thắng has agency: {agency.agency_name} (ID: {agency.agency_id})")
        except Agency.DoesNotExist:
            print(f"  ❌ ERROR: Thắng SHOULD have agency but none found")
            
    except User.DoesNotExist:
        print("❌ Thắng not found")

def check_database_integrity():
    """Check database integrity for agency assignments"""
    print("\n=== CHECKING DATABASE INTEGRITY ===")
    
    # Check for duplicate agency assignments
    agencies = Agency.objects.all()
    user_ids = []
    duplicates = []
    
    for agency in agencies:
        if agency.user_id:
            if agency.user_id in user_ids:
                duplicates.append(agency.user_id)
            user_ids.append(agency.user_id)
    
    if duplicates:
        print(f"❌ Found duplicate user_id assignments: {duplicates}")
    else:
        print("✓ No duplicate agency assignments found")
    
    # Check for orphaned agencies
    orphaned = Agency.objects.filter(user_id__isnull=False).exclude(
        user_id__in=User.objects.values_list('user_id', flat=True)
    )
    
    if orphaned.exists():
        print(f"❌ Found {orphaned.count()} orphaned agencies:")
        for agency in orphaned:
            print(f"  - {agency.agency_name} linked to non-existent user_id: {agency.user_id}")
    else:
        print("✓ No orphaned agencies found")

def generate_test_commands():
    """Generate test commands for manual testing"""
    print("\n=== MANUAL TEST COMMANDS ===")
    
    print("1. Test /auth/me/ API for Tuu:")
    print("   curl -X GET 'http://localhost:8000/api/v1/auth/me/' \\")
    print("        -H 'Cookie: access=<tuu_access_token>' \\")
    print("        -H 'Cache-Control: no-cache'")
    
    print("\n2. Test /auth/me/ API for Thắng:")
    print("   curl -X GET 'http://localhost:8000/api/v1/auth/me/' \\")
    print("        -H 'Cookie: access=<thang_access_token>' \\")
    print("        -H 'Cache-Control: no-cache'")
    
    print("\n3. Test agency API for agency ID 2 (Thắng's agency):")
    print("   curl -X GET 'http://localhost:8000/api/v1/agency/2/' \\")
    print("        -H 'Cookie: access=<token>' \\")
    print("        -H 'Cache-Control: no-cache'")
    
    print("\n4. Frontend test steps:")
    print("   a. Open browser Developer Tools (F12)")
    print("   b. Go to Application tab > Storage > Clear all data")
    print("   c. Go to Network tab > Check 'Disable cache'")
    print("   d. Login as 'Tuu' and check console logs")
    print("   e. Expected: See 'Chưa Được Phân Công Đại Lý' message")

if __name__ == '__main__':
    force_clear_django_cache()
    test_api_responses()
    check_database_integrity()
    generate_test_commands()
