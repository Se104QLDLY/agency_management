import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.contrib.auth.hashers import make_password

from authentication.models import Account, User

@pytest.fixture
def api_client():
    """
    Fixture for an anonymous API client.
    """
    return APIClient()

@pytest.fixture
def admin_user():
    """
    Fixture to create an admin user in the test database.
    """
    admin_account, created = Account.objects.get_or_create(
        username='pytest_admin',
        defaults={
            'password_hash': make_password('a_secure_password'),
            'account_role': Account.ADMIN
        }
    )
    admin_user, created = User.objects.get_or_create(
        account=admin_account,
        defaults={
            'full_name': 'Pytest Admin User',
            'email': 'pytest_admin@example.com',
        }
    )
    return admin_user

@pytest.fixture
def authenticated_admin_client(admin_user):
    """
    Fixture for an API client authenticated as an admin user.
    """
    client = APIClient()
    # Authenticate with the User object itself, not the related account.
    # Django's authentication backend will handle setting request.user correctly.
    client.force_authenticate(user=admin_user)
    return client 