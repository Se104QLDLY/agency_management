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

# --- AGENCY_04: GET /agency/<id>/ ---

def test_get_agency_detail_authenticated(authenticated_admin_client):
    """Retrieve specific agency detail (authenticated)"""
    from agency.models import AgencyType, District, Agency
    from datetime import date

    agency_type = AgencyType.objects.create(type_name="Type X", max_debt=1000000)
    district = District.objects.create(district_name="District X", max_agencies=10)
    agency = Agency.objects.create(
        agency_name="Detail Agency",
        agency_type=agency_type,
        phone_number="0987654321",
        address="1 Detail St",
        district=district,
        reception_date=date.today(),
        debt_amount=0
    )

    url = f"/api/v1/agency/{agency.agency_id}/"
    response = authenticated_admin_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == agency.agency_id
    assert response.data["name"] == "Detail Agency"


# --- AGENCY_05: PUT /agency/<id>/ ---

def test_update_agency_authenticated(authenticated_admin_client):
    """Update agency phone & address via PUT"""
    from agency.models import AgencyType, District, Agency
    from datetime import date

    agency_type = AgencyType.objects.create(type_name="Type Y", max_debt=2000000)
    district = District.objects.create(district_name="District Y", max_agencies=5)
    agency = Agency.objects.create(
        agency_name="Update Agency",
        agency_type=agency_type,
        phone_number="0123450000",
        address="Old Addr",
        district=district,
        reception_date=date.today(),
        debt_amount=0
    )

    url = f"/api/v1/agency/{agency.agency_id}/"
    payload = {
        "name": "Update Agency",
        "type_id": agency_type.agency_type_id,
        "phone": "0999999999",
        "address": "New Addr",
        "email": "update@example.com",
        "district_id": district.district_id
    }
    response = authenticated_admin_client.put(url, payload, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert response.data["phone"] == "0999999999"
    assert response.data["address"] == "New Addr"
    assert response.data["email"] == "update@example.com"


# --- AGENCY_06: DELETE /agency/<id>/ ---

def test_delete_agency_authenticated(authenticated_admin_client):
    """Delete agency and ensure it is removed"""
    from agency.models import AgencyType, District, Agency
    from datetime import date

    agency_type = AgencyType.objects.create(type_name="Type Z", max_debt=3000000)
    district = District.objects.create(district_name="District Z", max_agencies=3)
    agency = Agency.objects.create(
        agency_name="Delete Agency",
        agency_type=agency_type,
        phone_number="0777777777",
        address="Del Addr",
        district=district,
        reception_date=date.today(),
        debt_amount=0
    )

    url = f"/api/v1/agency/{agency.agency_id}/"
    response = authenticated_admin_client.delete(url)

    assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]

    # Verify the record is gone
    from agency.models import Agency
    assert not Agency.objects.filter(pk=agency.agency_id).exists()
