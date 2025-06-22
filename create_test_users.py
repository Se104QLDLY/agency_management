#!/usr/bin/env python
"""
Create test users for authentication testing
"""
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agency_management.settings')
django.setup()

from authentication.models import Account, User
from django.contrib.auth.hashers import make_password

def create_test_users():
    """Create test users for authentication testing"""
    print("Creating test users...")
    
    # Create admin user
    admin_account, created = Account.objects.get_or_create(
        username='admin',
        defaults={
            'password_hash': make_password('Admin123!'),
            'account_role': Account.ADMIN
        }
    )
    if created:
        admin_user = User.objects.create(
            account=admin_account,
            full_name='System Administrator',
            email='admin@example.com',
            phone_number='0901234567',
            address='123 Admin Street'
        )
        print(f"✓ Created admin user: {admin_user.full_name}")
    else:
        print("✓ Admin user already exists")

    # Create staff user
    staff_account, created = Account.objects.get_or_create(
        username='staff01',
        defaults={
            'password_hash': make_password('Staff123!'),
            'account_role': Account.STAFF
        }
    )
    if created:
        staff_user = User.objects.create(
            account=staff_account,
            full_name='Staff User',
            email='staff@example.com',
            phone_number='0901234568',
            address='456 Staff Avenue'
        )
        print(f"✓ Created staff user: {staff_user.full_name}")
    else:
        print("✓ Staff user already exists")

    # Create agent user
    agent_account, created = Account.objects.get_or_create(
        username='agent01',
        defaults={
            'password_hash': make_password('Agent123!'),
            'account_role': Account.AGENT
        }
    )
    if created:
        agent_user = User.objects.create(
            account=agent_account,
            full_name='Agent User',
            email='agent@example.com',
            phone_number='0901234569',
            address='789 Agent Road'
        )
        print(f"✓ Created agent user: {agent_user.full_name}")
    else:
        print("✓ Agent user already exists")

    print("\n=== Test Users Created ===")
    print("Admin Login: admin@example.com / Admin123!")
    print("Staff Login: staff@example.com / Staff123!")
    print("Agent Login: agent@example.com / Agent123!")
    print("\nOr use usernames: admin, staff01, agent01")

if __name__ == '__main__':
    create_test_users() 