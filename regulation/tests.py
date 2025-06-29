from django.test import TestCase
import pytest
from unittest.mock import Mock, patch, MagicMock
from regulation.models import Regulation
from authentication.models import User, Account
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

# Create your tests here.

@pytest.mark.django_db
class TestRegulationModel:
    """Test regulation model validation and methods"""
    
    def test_str_method(self):
        """Test string representation"""
        reg = Regulation(
            regulation_key="TEST_KEY",
            regulation_value="test_value"
        )
        assert str(reg) == "TEST_KEY: test_value"

    @patch('regulation.models.Regulation.validate_unique')
    def test_clean_valid_key(self, mock_validate_unique):
        """Test validation with valid key"""
        # Mock the unique validation to avoid database access
        mock_validate_unique.return_value = None
        
        reg = Regulation(
            regulation_key="VALID_KEY_123",
            regulation_value="valid_value"
        )
        # Should not raise exception
        reg.full_clean()

    def test_clean_invalid_key_special_characters(self):
        """Test validation with invalid key containing special characters"""
        reg = Regulation(
            regulation_key="INVALID-KEY!",
            regulation_value="valid_value"
        )
        with pytest.raises(Exception):
            reg.full_clean()

    def test_clean_empty_value(self):
        """Test validation with empty value"""
        reg = Regulation(
            regulation_key="VALID_KEY",
            regulation_value="   "
        )
        with pytest.raises(Exception):
            reg.full_clean()

@pytest.mark.django_db
class TestRegulationAPI:
    """Test regulation API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Setup test client and user"""
        self.client = APIClient()
        
        # Create account and user for authentication
        self.account = Account.objects.create(
            username="admin",
            password_hash="admin123_hashed",
            account_role=Account.ADMIN
        )
        
        self.user = User.objects.create(
            account=self.account,
            full_name="Admin User",
            email="admin@test.com"
        )
        
        self.client.force_authenticate(user=self.user)

    @patch('regulation.models.Regulation.objects.all')
    def test_list_regulations(self, mock_all):
        """Test listing regulations"""
        # Mock the queryset
        mock_regulation1 = Mock()
        mock_regulation1.regulation_key = "MAX_DEBT"
        mock_regulation1.regulation_value = "10000000"
        mock_regulation1.description = "Giới hạn nợ tối đa"
        mock_regulation1.updated_at = "2024-01-01T00:00:00Z"
        
        mock_regulation2 = Mock()
        mock_regulation2.regulation_key = "MIN_STOCK"
        mock_regulation2.regulation_value = "5"
        mock_regulation2.description = "Tồn kho tối thiểu"
        mock_regulation2.updated_at = "2024-01-01T00:00:00Z"
        
        mock_all.return_value = [mock_regulation1, mock_regulation2]
        
        url = reverse("regulation-list")
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        keys = [r["regulation_key"] for r in response.data]
        assert "MAX_DEBT" in keys
        assert "MIN_STOCK" in keys

    @patch('regulation.views.get_object_or_404')
    def test_get_regulation_detail(self, mock_get_object):
        """Test getting regulation detail"""
        mock_regulation = Mock()
        mock_regulation.regulation_key = "MAX_DEBT"
        mock_regulation.regulation_value = "10000000"
        mock_regulation.description = "Giới hạn nợ tối đa"
        mock_regulation.last_updated_by = self.user.user_id
        mock_regulation.updated_at = "2024-01-01T00:00:00Z"
        
        mock_get_object.return_value = mock_regulation
        
        url = reverse("regulation-detail", args=["MAX_DEBT"])
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["regulation_key"] == "MAX_DEBT"
        assert response.data["regulation_value"] == "10000000"

    @patch('regulation.serializers.RegulationUpdateSerializer.save')
    @patch('regulation.views.get_object_or_404')
    def test_update_regulation(self, mock_get_object, mock_serializer_save):
        """Test updating regulation"""
        mock_regulation = Mock()
        mock_regulation.regulation_key = "MAX_DEBT"
        mock_regulation.regulation_value = "10000000"
        mock_regulation.description = "Giới hạn nợ tối đa"
        mock_regulation.last_updated_by = self.user.user_id
        mock_regulation.updated_at = "2024-01-01T00:00:00Z"
        
        mock_get_object.return_value = mock_regulation
        mock_serializer_save.return_value = mock_regulation
        
        url = reverse("regulation-detail", args=["MAX_DEBT"])
        data = {"regulation_value": "20000000", "description": "Cập nhật giới hạn nợ"}
        response = self.client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        # Verify that serializer save was called
        mock_serializer_save.assert_called_once()

    @patch('regulation.views.get_object_or_404')
    def test_update_regulation_invalid_value(self, mock_get_object):
        """Test updating regulation with invalid value"""
        mock_regulation = Mock()
        mock_regulation.regulation_key = "MAX_DEBT"
        mock_regulation.regulation_value = "10000000"
        
        mock_get_object.return_value = mock_regulation
        
        url = reverse("regulation-detail", args=["MAX_DEBT"])
        data = {"regulation_value": "   "}  # Empty value
        response = self.client.put(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('regulation.models.Regulation.objects.all')
    def test_get_history(self, mock_all):
        """Test getting regulation history"""
        mock_regulation = Mock()
        mock_regulation.regulation_key = "MAX_DEBT"
        mock_regulation.regulation_value = "10000000"
        mock_regulation.last_updated_by = self.user.user_id
        mock_regulation.updated_at = "2024-01-01T00:00:00Z"
        
        mock_queryset = Mock()
        mock_queryset.order_by.return_value = [mock_regulation]
        mock_all.return_value = mock_queryset
        
        url = reverse("regulation-history")
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    @patch('regulation.models.Regulation.objects.all')
    def test_get_history_by_key(self, mock_all):
        """Test getting regulation history filtered by key"""
        mock_regulation = Mock()
        mock_regulation.regulation_key = "MAX_DEBT"
        mock_regulation.regulation_value = "10000000"
        mock_regulation.last_updated_by = self.user.user_id
        mock_regulation.updated_at = "2024-01-01T00:00:00Z"
        
        mock_queryset = Mock()
        mock_queryset.filter.return_value.order_by.return_value = [mock_regulation]
        mock_all.return_value = mock_queryset
        
        url = reverse("regulation-history")
        response = self.client.get(url, {"key": "MAX_DEBT"})
        
        assert response.status_code == status.HTTP_200_OK
        # Verify filter was called with correct key
        mock_queryset.filter.assert_called_with(regulation_key="MAX_DEBT")

    def test_permission_required(self):
        """Test that authentication is required"""
        # Remove authentication
        self.client.force_authenticate(user=None)
        url = reverse("regulation-list")
        response = self.client.get(url)
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    @patch('regulation.views.get_object_or_404')
    def test_not_found(self, mock_get_object):
        """Test getting non-existent regulation"""
        from django.http import Http404
        mock_get_object.side_effect = Http404
        
        url = reverse("regulation-detail", args=["NOT_EXIST"])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_urls_exist(self):
        """Test that URL patterns are properly configured"""
        # Test that URL patterns can be resolved
        list_url = reverse("regulation-list")
        detail_url = reverse("regulation-detail", args=["TEST_KEY"])
        history_url = reverse("regulation-history")
        
        assert list_url == "/api/v1/regulation/"
        assert detail_url == "/api/v1/regulation/TEST_KEY/"
        assert history_url == "/api/v1/regulation/history/"

    @patch('regulation.models.Regulation.objects.all')
    def test_serializer_fields(self, mock_all):
        """Test that serializers return correct fields"""
        mock_regulation = Mock()
        mock_regulation.regulation_key = "TEST_KEY"
        mock_regulation.regulation_value = "test_value"
        mock_regulation.description = "Test description"
        mock_regulation.updated_at = "2024-01-01T00:00:00Z"
        mock_regulation.last_updated_by = None
        
        mock_all.return_value = [mock_regulation]
        
        url = reverse("regulation-list")
        response = self.client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        if response.data:
            regulation_data = response.data[0]
            expected_fields = {'regulation_key', 'regulation_value', 'description', 'updated_at'}
            assert set(regulation_data.keys()) == expected_fields
