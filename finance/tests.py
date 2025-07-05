import pytest
from decimal import Decimal
from datetime import date, datetime
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
import json

from finance.models import Payment, Report, DebtSummary, SalesMonthly
from finance.services import FinanceService, DebtValidationService
from finance.views import PaymentViewSet, ReportViewSet, DebtViewSet
from agency.models import Agency, AgencyType, District
from authentication.models import User, Account
from inventory.models import Issue


@pytest.mark.django_db
class TestFinanceModels(TestCase):
    """Test finance models"""
    
    def test_payment_model_creation(self):
        """Test Payment model creation and validation"""
        payment = Payment(
            payment_id=1,
            payment_date=date.today(),
            agency_id=1,
            user_id=1,
            amount_collected=Decimal('100000')
        )
        # Thêm kiểm tra các trường bắt buộc
        assert payment.payment_id == 1
        assert payment.agency_id == 1
        assert payment.user_id == 1
        assert str(payment) == f"Payment #1 - Agency 1 - 100000"
        assert payment.amount_collected == Decimal('100000')
    
    def test_payment_clean_validation(self):
        """Test Payment clean() method validation"""
        # Create agency with debt
        agency_type = AgencyType.objects.create(
            type_name='Test Type',
            max_debt=Decimal('500000')
        )
        
        # Create a dummy district for the test
        district = District.objects.create(
            district_name='Test District',
            max_agencies=5
        )

        agency = Agency.objects.create(
            agency_name='Test Agency',
            agency_type=agency_type,
            phone_number='123456789',
            address='Test Address',
            district=district,
            reception_date=date.today(),
            debt_amount=Decimal('200000')
        )
        
        # Test valid payment
        payment = Payment(
            payment_id=1,
            payment_date=date.today(),
            agency_id=agency.agency_id,
            user_id=1, # Assuming a dummy user_id
            amount_collected=Decimal('100000')
        )
        payment.clean()  # Should not raise exception
        
        # Test payment exceeding debt
        payment.amount_collected = Decimal('300000')
        with pytest.raises(Exception):  # ValidationError
            payment.clean()
    
    def test_report_model_creation(self):
        """Test Report model creation"""
        report = Report(
            report_id=1,
            report_type='sales',
            report_date=date.today(),
            data={'test': 'data'},
            created_by=1
        )
        assert "Report #1" in str(report)
        assert report.report_type == 'sales'
    
    def test_debt_summary_model(self):
        """Test DebtSummary model (view model)"""
        debt_summary = DebtSummary(
            agency_id=1,
            agency_name='Test Agency',
            debt_amount=Decimal('150000')
        )
        assert debt_summary.agency_id == 1
        assert debt_summary.debt_amount == Decimal('150000')
    
    def test_sales_monthly_model(self):
        """Test SalesMonthly model (view model)"""
        sales_monthly = SalesMonthly(
            month='2025-01',
            total_sales=Decimal('500000')
        )
        assert sales_monthly.month == '2025-01'
        assert sales_monthly.total_sales == Decimal('500000')


@pytest.mark.django_db
class TestFinanceServices:
    """Test finance business logic services"""
    
    def setup_method(self):
        """Setup test data"""
        # Create agency type
        self.agency_type = AgencyType.objects.create(
            type_name='Test Type',
            max_debt=Decimal('1000000')
        )
        
        # Create a dummy district
        self.district = District.objects.create(
            district_name='Test District',
            max_agencies=5
        )

        # Create agency
        self.agency = Agency.objects.create(
            agency_name='Test Agency',
            agency_type=self.agency_type,
            phone_number='123456789',
            address='Test Address',
            district=self.district,
            reception_date=date.today(),
            debt_amount=Decimal('500000')
        )
        
        # Create user
        account = Account.objects.create_user(
            username='testuser',
            password_hash='a_secure_hash', # In tests, the hash can be simple
            account_role=Account.STAFF
        )
        self.user = User.objects.create(
            account=account,
            full_name='Test User'
        )
    
    def test_create_payment_success(self):
        """Test successful payment creation"""
        payment_data = {
            'agency_id': self.agency.agency_id,
            'amount_collected': '200000',
            'payment_date': date.today()
        }
        # Đảm bảo truyền đúng user_id
        payment, debt_info = FinanceService.create_payment(payment_data, self.user)
        assert payment.agency_id == self.agency.agency_id
        assert payment.amount_collected == Decimal('200000')
        assert payment.user_id == self.user.account.account_id
        
        # Check debt info
        assert debt_info['previous_debt'] == Decimal('500000')
        assert debt_info['payment_amount'] == Decimal('200000')
        assert debt_info['new_debt_balance'] == Decimal('300000')
        assert not debt_info['is_credit']
        
        # Check agency debt updated
        self.agency.refresh_from_db()
        assert self.agency.debt_amount == Decimal('300000')
    
    def test_create_payment_invalid_amount(self):
        """Test payment with invalid amount"""
        payment_data = {
            'agency_id': self.agency.agency_id,
            'amount_collected': '0'
        }
        
        with pytest.raises(Exception):  # BusinessRuleViolation
            FinanceService.create_payment(payment_data, self.user)
    
    def test_create_payment_agency_not_found(self):
        """Test payment for non-existent agency"""
        payment_data = {
            'agency_id': 999,
            'amount_collected': '100000'
        }
        
        with pytest.raises(ValueError):
            FinanceService.create_payment(payment_data, self.user)
    
    def test_create_payment_credit_balance(self):
        """Test payment creating credit balance"""
        payment_data = {
            'agency_id': self.agency.agency_id,
            'amount_collected': '600000'  # More than debt
        }
        
        payment, debt_info = FinanceService.create_payment(payment_data, self.user)
        
        assert debt_info['is_credit']
        assert debt_info['credit_amount'] == Decimal('100000')
        assert debt_info['new_debt_balance'] == Decimal('-100000')
    
    def test_get_debt_summary(self):
        """Test debt summary service"""
        summary = FinanceService.get_debt_summary()
        
        assert len(summary) >= 1
        agency_summary = summary[0]
        assert agency_summary['agency_id'] == self.agency.agency_id
        assert agency_summary['agency_name'] == 'Test Agency'
        assert agency_summary['current_debt'] == 500000.0
        assert agency_summary['debt_limit'] == 1000000.0
        assert agency_summary['debt_utilization_percent'] == 50.0
    
    def test_get_debt_aging_analysis(self):
        """Test debt aging analysis"""
        aging_data = FinanceService.get_debt_aging_analysis()
        
        assert len(aging_data) >= 1
        agency_aging = aging_data[0]
        assert agency_aging['agency_id'] == self.agency.agency_id
        assert agency_aging['debt_amount'] == 500000.0
        assert 'aging_category' in agency_aging
    
    def test_can_issue_to_agency(self):
        """Test debt validation service"""
        # Test can issue within limit
        can_issue, _ = DebtValidationService.can_issue_to_agency(self.agency.agency_id, Decimal('200000'))
        assert can_issue
        
        # Test cannot issue over limit
        can_issue, _ = DebtValidationService.can_issue_to_agency(self.agency.agency_id, Decimal('600000'))
        assert not can_issue
    
    def test_get_agencies_near_limit(self):
        """Test getting agencies near debt limit"""
        agencies = DebtValidationService.get_agencies_near_limit(threshold_percent=90)
        # Should return agencies with debt > 90% of limit
        assert isinstance(agencies, list)


@pytest.mark.django_db
class TestFinanceAPIs:
    """Test finance API endpoints"""
    
    def setup_method(self):
        """Setup test data and client"""
        self.client = APIClient()
        
        # Create agency type
        self.agency_type = AgencyType.objects.create(
            type_name='Test Type',
            max_debt=Decimal('1000000')
        )
        
        # Create a dummy district
        self.district = District.objects.create(
            district_name='Test District',
            max_agencies=5
        )

        # Create agency
        self.agency = Agency.objects.create(
            agency_name='Test Agency',
            agency_type=self.agency_type,
            phone_number='123456789',
            address='Test Address',
            district=self.district,
            reception_date=date.today(),
            debt_amount=Decimal('500000')
        )
        
        # Create user
        account = Account.objects.create_user(
            username='testuser', 
            password_hash='a_secure_hash',
            account_role=Account.STAFF
        )
        self.user = User.objects.create(
            account=account,
            full_name='Test User'
        )
        self.client.force_authenticate(user=self.user.account)

    def test_payment_list_api(self):
        """Test payment list API"""
        url = reverse('payment-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_payment_create_api(self):
        """Test payment create API"""
        url = reverse('payment-list')
        data = {
            'agency_id': self.agency.agency_id,
            'payment_date': date.today(),
            'amount_collected': '100000'
        }
        response = self.client.post(url, data)
        # Nếu trả về 500, in log chi tiết
        if response.status_code == 500:
            print('API error:', response.data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['payment']['amount_collected'] == '100000.00'

    def test_payment_detail_api(self):
        """Test payment detail API"""
        payment = Payment.objects.create(
            agency_id=self.agency.agency_id,
            user_id=self.user.account.account_id,
            payment_date=date.today(),
            amount_collected=Decimal('50000')
        )
        url = reverse('payment-detail', kwargs={'pk': payment.pk})
        response = self.client.get(url)
        if response.status_code == 500:
            print('API error:', response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['amount_collected'] == '50000.00'

    def test_report_list_api(self):
        """Test report list API"""
        url = reverse('report-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_report_create_api(self):
        """Test report create API"""
        url = reverse('report-list')
        data = {
            'report_type': 'debt',
            'report_date': date.today(),
            'data': {'info': 'test report'}
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['report_type'] == 'debt'

    def test_debt_list_api(self):
        """Test debt list API"""
        url = reverse('debt-list')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_debt_summary_api(self):
        """Test debt summary API"""
        url = reverse('debt-summary')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_debt_aging_api(self):
        """Test debt aging API"""
        url = reverse('debt-aging')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_payment_filters(self):
        """Test payment filtering"""
        url = f"{reverse('payment-list')}?agency_id={self.agency.agency_id}"
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestFinanceViewSets:
    """Test finance viewsets"""

    def setup_method(self):
        """Setup for viewset tests"""
        self.client = APIClient()

        # Create agency type
        self.agency_type = AgencyType.objects.create(
            type_name='Test Type',
            max_debt=Decimal('1000000')
        )

        # Create a dummy district
        self.district = District.objects.create(
            district_name='Test District',
            max_agencies=5
        )

        # Create agency
        self.agency = Agency.objects.create(
            agency_name='Test Agency',
            agency_type=self.agency_type,
            phone_number='123456789',
            address='Test Address',
            district=self.district,
            reception_date=date.today(),
            debt_amount=Decimal('500000')
        )
        
        # Create user
        account = Account.objects.create_user(
            username='testuser', 
            password_hash='a_secure_hash',
            account_role=Account.STAFF
        )
        self.user = User.objects.create(
            account=account,
            full_name='Test User'
        )
        self.client.force_authenticate(user=self.user.account)

    def test_payment_viewset_serializer_classes(self):
        """Test serializer classes for PaymentViewSet"""
        view = PaymentViewSet()
        
        view.action = 'list'
        assert view.get_serializer_class() is not None

        view.action = 'create'
        assert view.get_serializer_class() is not None

        view.action = 'retrieve'
        assert view.get_serializer_class() is not None

    def test_report_viewset_serializer_classes(self):
        """Test serializer classes for ReportViewSet"""
        view = ReportViewSet()

        view.action = 'list'
        assert view.get_serializer_class() is not None

        view.action = 'create'
        assert view.get_serializer_class() is not None

        view.action = 'retrieve'
        assert view.get_serializer_class() is not None


@pytest.mark.django_db
class TestFinanceIntegration:
    """Test finance integration scenarios"""

    def setup_method(self):
        """Setup for integration tests"""
        self.client = APIClient()

        # Create agency type
        self.agency_type = AgencyType.objects.create(
            type_name='Test Type',
            max_debt=Decimal('1000000')
        )
        
        # Create a dummy district
        self.district = District.objects.create(
            district_name='Test District',
            max_agencies=5
        )

        # Create agency
        self.agency = Agency.objects.create(
            agency_name='Test Agency',
            agency_type=self.agency_type,
            phone_number='123456789',
            address='Test Address',
            district=self.district,
            reception_date=date.today(),
            debt_amount=Decimal('500000')
        )
        
        # Create user and authenticate
        account = Account.objects.create_user(
            username='testuser', 
            password_hash='a_secure_hash',
            account_role=Account.STAFF
        )
        self.user = User.objects.create(
            account=account,
            full_name='Test User'
        )
        self.client.force_authenticate(user=self.user.account)

    def test_payment_workflow(self):
        """Test a full payment workflow"""
        # 1. Check initial debt
        assert self.agency.debt_amount == Decimal('500000')
        
        # 2. Make a payment via API
        url = reverse('payment-list')
        data = {
            'agency_id': self.agency.agency_id,
            'payment_date': date.today(),
            'amount_collected': '150000'
        }
        response = self.client.post(url, data)
        if response.status_code == 500:
            print('API error:', response.data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # 3. Verify debt is updated
        self.agency.refresh_from_db()
        assert self.agency.debt_amount == Decimal('350000')

    def test_debt_validation_workflow(self):
        """Test debt validation during issue creation"""
        # 1. Check current debt
        assert self.agency.debt_amount == Decimal('500000')
        
        # 2. Try to issue goods that exceed the debt limit
        can_issue, _ = DebtValidationService.can_issue_to_agency(self.agency.agency_id, Decimal('600000'))
        assert not can_issue
        
        # 3. Issue goods within the limit
        can_issue, _ = DebtValidationService.can_issue_to_agency(self.agency.agency_id, Decimal('400000'))
        assert can_issue


@pytest.fixture
def agency_type():
    """Create agency type fixture"""
    return AgencyType.objects.create(
        type_name='Test Type',
        max_debt=Decimal('1000000')
    )

@pytest.fixture
def agency(agency_type):
    """Create agency fixture"""
    district = District.objects.create(district_name="Test District", max_agencies=10)
    return Agency.objects.create(
        agency_name='Test Agency',
        agency_type=agency_type,
        phone_number='123456789',
        address='Test Address',
        district=district,
        reception_date=date.today(),
        debt_amount=Decimal('500000')
    )

@pytest.fixture
def user():
    """Create user fixture"""
    account = Account.objects.create_user(
        username='fixtureuser',
        password_hash='a_secure_hash',
        account_role=Account.STAFF
    )
    return User.objects.create(account=account, full_name="Fixture User")

@pytest.fixture
def api_client(user):
    """Create API client and authenticate user"""
    client = APIClient()
    client.force_authenticate(user=user.account)
    return client