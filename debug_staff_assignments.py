#!/usr/bin/env python3
"""
Script to debug and clean staff agency assignments
"""
import os
import sys
import django

# Add the Django project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agency_management.settings')
django.setup()

from agency.models import StaffAgency, Agency
from authentication.models import User, Account

def debug_staff_assignments():
    """Debug staff assignments in the database"""
    print("=== DEBUGGING STAFF AGENCY ASSIGNMENTS ===")
    
    # Get all staff users
    staff_accounts = Account.objects.filter(account_role='staff')
    print(f"Total staff accounts: {staff_accounts.count()}")
    
    for account in staff_accounts:
        try:
            user = User.objects.get(account=account)
            print(f"\nStaff: {account.username} (ID: {user.user_id})")
            
            # Check assignments
            assignments = StaffAgency.objects.filter(staff_id=user.user_id)
            print(f"Assignments count: {assignments.count()}")
            
            for assignment in assignments:
                print(f"  - Agency: {assignment.agency.agency_name} (ID: {assignment.agency.agency_id})")
                
        except User.DoesNotExist:
            print(f"User not found for account: {account.username}")

def clean_staff_assignments(staff_username=None):
    """Clean specific staff assignments"""
    if not staff_username:
        print("Please provide staff username to clean")
        return
        
    try:
        account = Account.objects.get(username=staff_username)
        user = User.objects.get(account=account)
        
        assignments = StaffAgency.objects.filter(staff_id=user.user_id)
        count = assignments.count()
        
        print(f"Found {count} assignments for staff {staff_username}")
        
        if count > 0:
            confirm = input(f"Delete all {count} assignments? (y/N): ")
            if confirm.lower() == 'y':
                assignments.delete()
                print(f"Deleted {count} assignments")
            else:
                print("Cancelled")
        else:
            print("No assignments to clean")
            
    except Account.DoesNotExist:
        print(f"Staff username '{staff_username}' not found")
    except User.DoesNotExist:
        print(f"User not found for account: {staff_username}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'debug':
            debug_staff_assignments()
        elif sys.argv[1] == 'clean' and len(sys.argv) > 2:
            clean_staff_assignments(sys.argv[2])
        else:
            print("Usage:")
            print("  python debug_staff_assignments.py debug")
            print("  python debug_staff_assignments.py clean <staff_username>")
    else:
        debug_staff_assignments()
