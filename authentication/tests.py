import pytest
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import Account, User
from authentication.serializers import LoginSerializer, UserProfileSerializer


@pytest.mark.django_db
class TestAccountModel:
    """Test cases cơ bản cho Account model"""

    def test_create_account_success(self):
        """Kiểm tra tạo account thành công"""
        account = Account.objects.create(
            username='testuser',
            password_hash=make_password('testpass123'),
            account_role=Account.ADMIN
        )
        assert account.username == 'testuser'
        assert account.account_role == Account.ADMIN
        assert account.created_at is not None

    def test_account_username_unique(self):
        """Kiểm tra username phải là duy nhất"""
        Account.objects.create(
            username='testuser',
            password_hash=make_password('testpass123'),
            account_role=Account.ADMIN
        )
        with pytest.raises(IntegrityError):
            Account.objects.create(
                username='testuser',
                password_hash=make_password('anotherpass'),
                account_role=Account.STAFF
            )

    def test_account_str_representation(self):
        """Kiểm tra string representation của Account"""
        account = Account.objects.create(
            username='testuser',
            password_hash=make_password('testpass123'),
            account_role=Account.ADMIN
        )
        expected_str = f"{account.username} ({account.account_role})"
        assert str(account) == expected_str


@pytest.mark.django_db
class TestUserModel:
    """Test cases cơ bản cho User model"""

    @pytest.fixture
    def account(self):
        """Fixture tạo account cho test"""
        return Account.objects.create(
            username='testuser',
            password_hash=make_password('testpass123'),
            account_role=Account.AGENT
        )

    def test_create_user_success(self, account):
        """Kiểm tra tạo user thành công"""
        user = User.objects.create(
            account=account,
            full_name='Test User',
            email='test@example.com',
            phone_number='0123456789'
        )
        assert user.full_name == 'Test User'
        assert user.email == 'test@example.com'
        assert user.phone_number == '0123456789'

    def test_user_email_unique(self, account):
        """Kiểm tra email phải là duy nhất"""
        User.objects.create(
            account=account,
            full_name='Test User',
            email='test@example.com',
            phone_number='0123456789'
        )
        
        another_account = Account.objects.create(
            username='anotheruser',
            password_hash=make_password('testpass'),
            account_role=Account.STAFF
        )
        with pytest.raises(IntegrityError):
            User.objects.create(
                account=another_account,
                full_name='Another User',
                email='test@example.com'
            )

    def test_user_str_representation(self, account):
        """Kiểm tra string representation của User"""
        user = User.objects.create(
            account=account,
            full_name='Test User',
            email='test@example.com',
            phone_number='0123456789'
        )
        assert str(user) == 'Test User'


@pytest.mark.django_db
class TestAuthenticationAPI:
    """Test cases cơ bản cho API authentication"""

    @pytest.fixture
    def api_client(self):
        """Fixture tạo APIClient"""
        return APIClient()

    @pytest.fixture
    def user(self):
        """Fixture tạo user cho test"""
        account = Account.objects.create(
            username='testuser',
            password_hash=make_password('testpass123'),
            account_role=Account.AGENT
        )
        return User.objects.create(
            account=account,
            full_name='Test User',
            email='test@example.com',
            phone_number='0123456789'
        )

    def test_login_success(self, api_client, user):
        """Kiểm tra login thành công"""
        from django.urls import reverse
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'user' in response.data

    def test_login_invalid_credentials(self, api_client, user):
        """Kiểm tra login với thông tin sai"""
        from django.urls import reverse
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = api_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_current_user_get(self, api_client, user):
        """Kiểm tra lấy thông tin user hiện tại"""
        from django.urls import reverse
        # Tạo access token
        refresh = RefreshToken()
        refresh['user_id'] = user.user_id
        access_token = refresh.access_token
        
        url = reverse('current-user')
        api_client.cookies['access'] = str(access_token)
        
        response = api_client.get(url, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['full_name'] == 'Test User'


@pytest.mark.django_db
class TestDatabaseConstraints:
    """Kiểm tra các ràng buộc database"""

    def test_account_role_check_constraint(self):
        """Kiểm tra ràng buộc check cho account_role"""
        with pytest.raises(IntegrityError):
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO auth.account (username, password_hash, account_role)
                    VALUES ('testuser', 'hash', 'invalid_role')
                """)

    def test_foreign_key_constraint_user_account(self):
        """Kiểm tra ràng buộc foreign key giữa user và account"""
        with pytest.raises(IntegrityError):
            User.objects.create(
                account_id=999,  # Account không tồn tại
                full_name='Test User',
                email='test@example.com'
            ) 