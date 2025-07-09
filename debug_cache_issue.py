#!/usr/bin/env python3
"""
Script to debug user authentication and agency assignment issues
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
from agency.models import Agency, StaffAgency

def debug_user_data():
    """Debug specific user data to identify cache issues"""
    print("=== DEBUGGING USER DATA FOR CACHE ISSUES ===")
    
    # Check if we have users named "Tuu" and "Xuân Thắng"
    users = User.objects.select_related('account').all()
    
    print(f"\nTotal users in system: {users.count()}")
    
    for user in users:
        print(f"\n--- User: {user.full_name} ---")
        print(f"  User ID: {user.user_id}")
        print(f"  Username: {user.account.username}")
        print(f"  Role: {user.account.account_role}")
        print(f"  Email: {user.email}")
        
        # Check agency assignments
        if user.account.account_role == 'agent':
            try:
                agency = Agency.objects.get(user_id=user.user_id)
                print(f"  Agent linked to agency: {agency.agency_name} (ID: {agency.agency_id})")
            except Agency.DoesNotExist:
                print(f"  Agent NOT linked to any agency")
        
        elif user.account.account_role == 'staff':
            assignments = StaffAgency.objects.filter(staff_id=user.user_id)
            if assignments.exists():
                print(f"  Staff assigned to {assignments.count()} agencies:")
                for assignment in assignments:
                    print(f"    - {assignment.agency.agency_name} (ID: {assignment.agency.agency_id})")
            else:
                print(f"  Staff NOT assigned to any agency")

def find_user_issues():
    """Find potential issues with user assignments"""
    print("\n=== FINDING POTENTIAL ISSUES ===")
    
    # Find agents without agencies
    agent_accounts = Account.objects.filter(account_role='agent')
    agents_without_agency = []
    
    for account in agent_accounts:
        try:
            user = User.objects.get(account=account)
            try:
                Agency.objects.get(user_id=user.user_id)
            except Agency.DoesNotExist:
                agents_without_agency.append(user)
        except User.DoesNotExist:
            continue
    
    if agents_without_agency:
        print(f"\n⚠️  Found {len(agents_without_agency)} agents without agencies:")
        for user in agents_without_agency:
            print(f"  - {user.full_name} (ID: {user.user_id}, Username: {user.account.username})")
    
    # Find staff without assignments
    staff_accounts = Account.objects.filter(account_role='staff')
    staff_without_assignments = []
    
    for account in staff_accounts:
        try:
            user = User.objects.get(account=account)
            assignments = StaffAgency.objects.filter(staff_id=user.user_id)
            if not assignments.exists():
                staff_without_assignments.append(user)
        except User.DoesNotExist:
            continue
    
    if staff_without_assignments:
        print(f"\n⚠️  Found {len(staff_without_assignments)} staff without assignments:")
        for user in staff_without_assignments:
            print(f"  - {user.full_name} (ID: {user.user_id}, Username: {user.account.username})")

def check_specific_users():
    """Check for specific users mentioned in the issue"""
    print("\n=== CHECKING SPECIFIC USERS ===")
    
    # Look for users that might be "Tuu" or "Xuân Thắng"
    search_names = ['Tuu', 'Thắng', 'Thang', 'Xuân']
    
    for name in search_names:
        users = User.objects.filter(full_name__icontains=name)
        if users.exists():
            print(f"\nUsers containing '{name}':")
            for user in users:
                print(f"  - {user.full_name} (ID: {user.user_id}, Username: {user.account.username}, Role: {user.account.account_role})")
                
                if user.account.account_role == 'agent':
                    try:
                        agency = Agency.objects.get(user_id=user.user_id)
                        print(f"    Linked to agency: {agency.agency_name}")
                    except Agency.DoesNotExist:
                        print(f"    NOT linked to any agency")

def create_test_scenario():
    """Create a test scenario to reproduce the issue"""
    print("\n=== CREATING TEST SCENARIO ===")
    
    # Check if we can create test users to reproduce the issue
    test_usernames = ['test_tuu', 'test_thang']
    
    for username in test_usernames:
        try:
            account = Account.objects.get(username=username)
            user = User.objects.get(account=account)
            print(f"Test user {username} already exists: {user.full_name} (ID: {user.user_id})")
        except (Account.DoesNotExist, User.DoesNotExist):
            print(f"Test user {username} does not exist - would need to create")

if __name__ == '__main__':
    debug_user_data()
    find_user_issues()
    check_specific_users()
    create_test_scenario()
