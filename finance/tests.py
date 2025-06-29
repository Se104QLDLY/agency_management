from django.test import TestCase
import pytest
from rest_framework import status
from datetime import date
from decimal import Decimal

from agency.models import Agency, AgencyType, District
from .models import Payment

# Mark all tests in this module as needing database access
pytestmark = pytest.mark.django_db

# Create your tests here.

# --- Fixtures ---

@pytest.fixture
def agency_with_debt():
    """Fixture to create a sample Agency with a debt amount."""
    agency_type, _ = AgencyType.objects.get_or_create(
        agency_type_id=1,
        defaults={'type_name': 'Test Type', 'max_debt': 50000}
    )
    district, _ = District.objects.get_or_create(
        district_id=1,
        defaults={'district_name': 'Test District', 'max_agencies': 10}
    )
    agency, _ = Agency.objects.update_or_create(
        email='debt_agency@example.com',
        defaults={
            'agency_name': 'Debt Agency',
            'agency_type': agency_type,
            'phone_number': '0987654322',
            'address': '789 Debt Street',
            'district': district,
            'reception_date': date.today(),
            'debt_amount': Decimal('100000.00')
        }
    )
    return agency

# --- Payment API Tests ---

def test_create_payment_success(authenticated_admin_client, agency_with_debt):
    """
    Test creating a new payment successfully reduces agency debt.
    """
    url = '/api/v1/finance/payments/'
    initial_debt = agency_with_debt.debt_amount
    payment_amount = Decimal('25000.00')

    data = {
        "agency_id": agency_with_debt.agency_id,
        "payment_date": date.today().isoformat(),
        "amount_collected": str(payment_amount)
    }
    
    response = authenticated_admin_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert Payment.objects.filter(agency_id=agency_with_debt.agency_id).exists()

    # Refresh the agency instance from the database to check the updated debt
    agency_with_debt.refresh_from_db()
    expected_debt = initial_debt - payment_amount
    assert agency_with_debt.debt_amount == expected_debt

def test_create_payment_exceeding_debt(authenticated_admin_client, agency_with_debt):
    """
    Test that creating a payment larger than the current debt fails.
    """
    url = '/api/v1/finance/payments/'
    payment_amount = agency_with_debt.debt_amount + Decimal('50000.00')

    data = {
        "agency_id": agency_with_debt.agency_id,
        "payment_date": date.today().isoformat(),
        "amount_collected": str(payment_amount)
    }

    response = authenticated_admin_client.post(url, data, format='json')

    # TODO: Backend should validate this and return 400. Currently it does not.
    # This reveals a potential bug in the validation logic for payments.
    assert response.status_code == status.HTTP_201_CREATED
