import pytest
from rest_framework import status

# Mark all tests in this module as needing database access
pytestmark = pytest.mark.django_db

# --- Agency Endpoints ---

def test_list_agencies_authenticated(authenticated_admin_client):
    """
    Test listing all agencies for an authenticated admin user.
    """
    url = '/api/v1/agency/'
    response = authenticated_admin_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in response.data
    assert 'count' in response.data

def test_list_agencies_unauthenticated(api_client):
    """
    Test that unauthenticated users receive a 401 Unauthorized error.
    """
    url = '/api/v1/agency/'
    response = api_client.get(url)
    # Based on HttpOnly cookie auth, this should result in an error
    # The exact error can be 401 or 403 depending on configuration
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

def test_create_agency(authenticated_admin_client):
    """
    Test creating a new agency.
    This test assumes that AgencyType with id=1 and District with id=1 exist.
    A more robust test would create these dependencies first.
    """
    url = '/api/v1/agency/'
    
    # Pre-requisite: Create AgencyType and District or ensure they exist
    # Use the correct primary key fields: agency_type_id and district_id
    from agency.models import AgencyType, District
    from datetime import date
    agency_type, _ = AgencyType.objects.get_or_create(
        agency_type_id=1, 
        defaults={'type_name': 'Test Type', 'max_debt': 50000}
    )
    district, _ = District.objects.get_or_create(
        district_id=1, 
        defaults={'district_name': 'Test District', 'max_agencies': 10}
    )
    
    data = {
        "name": "PyTest Central Agency",
        "type_id": agency_type.agency_type_id,
        "phone": "0123456789",
        "address": "123 Pytest Lane",
        "district_id": district.district_id,
        "email": "pytest@central.com"
    }
    response = authenticated_admin_client.post(url, data, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == "PyTest Central Agency"
    assert 'id' in response.data

# --- AgencyType and District Endpoints ---

def test_list_agency_types(authenticated_admin_client):
    """
    Test listing all agency types.
    """
    url = '/api/v1/agency-types/'
    response = authenticated_admin_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in response.data

def test_list_districts(authenticated_admin_client):
    """
    Test listing all districts.
    """
    url = '/api/v1/districts/'
    response = authenticated_admin_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in response.data
