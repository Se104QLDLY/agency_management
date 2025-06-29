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

@pytest.fixture
def sample_regulation():
    """
    Fixture to create a sample regulation for testing.
    """
    from regulation.models import Regulation
    regulation = Regulation.objects.create(
        regulation_key='SAMPLE_KEY',
        regulation_value='Sample Value',
        description='Sample description'
    )
    return regulation

@pytest.fixture
def regulation_with_updater(admin_user):
    """
    Fixture to create a regulation with an updater user.
    """
    from regulation.models import Regulation
    regulation = Regulation.objects.create(
        regulation_key='UPDATER_KEY',
        regulation_value='Updater Value',
        description='Regulation with updater',
        last_updated_by=admin_user.user_id
    )
    return regulation

@pytest.fixture
def multiple_regulations():
    """
    Fixture to create multiple regulations for testing ordering and queries.
    """
    from regulation.models import Regulation
    regulations = [
        Regulation.objects.create(
            regulation_key='MAX_LOGIN_ATTEMPTS',
            regulation_value='5',
            description='Maximum number of login attempts'
        ),
        Regulation.objects.create(
            regulation_key='SESSION_TIMEOUT',
            regulation_value='30',
            description='Session timeout in minutes'
        ),
        Regulation.objects.create(
            regulation_key='PASSWORD_MIN_LENGTH',
            regulation_value='8',
            description='Minimum password length'
        ),
        Regulation.objects.create(
            regulation_key='ENABLE_2FA',
            regulation_value='true',
            description='Enable two-factor authentication'
        )
    ]
    return regulations 