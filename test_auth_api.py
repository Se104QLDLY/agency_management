#!/usr/bin/env python
"""
Test script for Authentication API
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
import requests
import json

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

def test_auth_endpoints():
    """Test authentication endpoints"""
    base_url = 'http://localhost:8000/api/v1'
    
    print("\n=== Testing Authentication API ===")
    
    # Test 1: Login with email
    print("\n1. Testing login with email...")
    login_data = {
        'email': 'admin@example.com',
        'password': 'Admin123!'
    }
    
    response = requests.post(f'{base_url}/auth/login/', json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Login successful")
        data = response.json()
        print(f"User: {data['user']['full_name']} ({data['user']['account_role']})")
        # Save cookies for next requests
        cookies = response.cookies
    else:
        print(f"✗ Login failed: {response.text}")
        return
    
    # Test 2: Get current user profile
    print("\n2. Testing current user profile...")
    response = requests.get(f'{base_url}/auth/me/', cookies=cookies)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Profile retrieved successfully")
        data = response.json()
        print(f"Profile: {data['full_name']} - {data['email']}")
    else:
        print(f"✗ Profile retrieval failed: {response.text}")
    
    # Test 3: List users (admin only)
    print("\n3. Testing user list (admin access)...")
    response = requests.get(f'{base_url}/users/', cookies=cookies)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Users list retrieved successfully")
        data = response.json()
        print(f"Total users: {data['count']}")
        for user in data['results'][:3]:  # Show first 3
            print(f"- {user['full_name']} ({user['account_role']})")
    else:
        print(f"✗ Users list failed: {response.text}")
    
    # Test 4: Registration
    print("\n4. Testing user registration...")
    register_data = {
        'username': 'testuser',
        'password': 'Test123!',
        'confirm_password': 'Test123!',
        'full_name': 'Test User',
        'email': 'test@example.com',
        'phone_number': '0901234570',
        'address': '123 Test Street',
        'account_role': 'agent'
    }
    
    response = requests.post(f'{base_url}/auth/register/', json=register_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("✓ Registration successful")
        data = response.json()
        print(f"New user: {data['user']['full_name']}")
    else:
        print(f"✗ Registration failed: {response.text}")
    
    # Test 5: Login with username
    print("\n5. Testing login with username...")
    login_data = {
        'username': 'staff01',
        'password': 'Staff123!'
    }
    
    response = requests.post(f'{base_url}/auth/login/', json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Username login successful")
        data = response.json()
        print(f"User: {data['user']['full_name']} ({data['user']['account_role']})")
    else:
        print(f"✗ Username login failed: {response.text}")
    
    # Test 6: Token refresh
    print("\n6. Testing token refresh...")
    response = requests.post(f'{base_url}/auth/refresh/', cookies=cookies)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Token refresh successful")
    else:
        print(f"✗ Token refresh failed: {response.text}")
    
    # Test 7: Logout
    print("\n7. Testing logout...")
    response = requests.post(f'{base_url}/auth/logout/', cookies=cookies)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Logout successful")
    else:
        print(f"✗ Logout failed: {response.text}")

def main():
    print("=== Authentication API Test Suite ===")
    
    # Create test users
    create_test_users()
    
    # Test API endpoints
    try:
        test_auth_endpoints()
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to server. Make sure Django dev server is running:")
        print("python manage.py runserver")
        return
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        return
    
    print("\n=== Test completed ===")

if __name__ == '__main__':
    main() 