import pytest
from rest_framework import status

# Mark all tests in this module as needing database access
pytestmark = pytest.mark.django_db

# --- Authentication Endpoints ---

def test_login_success(api_client, admin_user):
    """
    Test successful login with correct credentials.
    """
    url = '/api/v1/auth/login/'
    data = {'username': 'pytest_admin', 'password': 'a_secure_password'}
    response = api_client.post(url, data, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert 'user' in response.data
    assert response.data['user']['username'] == 'pytest_admin'
    assert 'access' in response.cookies # Check if HttpOnly cookie is set

def test_login_failure(api_client, admin_user):
    """
    Test failed login with incorrect credentials.
    """
    url = '/api/v1/auth/login/'
    data = {'username': 'pytest_admin', 'password': 'wrong_password'}
    response = api_client.post(url, data, format='json')

    # The API returns 400 on failed login attempt, which is a valid design choice.
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_current_user_authenticated(authenticated_admin_client):
    """
    Test retrieving the current user's profile when authenticated.
    """
    url = '/api/v1/auth/me/'
    response = authenticated_admin_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == 'pytest_admin'

def test_get_current_user_unauthenticated(api_client):
    """
    Test that an unauthenticated user cannot retrieve a profile.
    """
    url = '/api/v1/auth/me/'
    response = api_client.get(url)

    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

def test_logout(api_client, admin_user):
    """
    Test that a user can log out, and the session is terminated.
    """
    login_url = '/api/v1/auth/login/'
    login_data = {'username': 'pytest_admin', 'password': 'a_secure_password'}
    
    # Log in first
    login_response = api_client.post(login_url, login_data, format='json')
    assert login_response.status_code == status.HTTP_200_OK

    # Now, log out
    logout_url = '/api/v1/auth/logout/'
    logout_response = api_client.post(logout_url, format='json')
    assert logout_response.status_code == status.HTTP_200_OK

    # Verify session is terminated by trying to access a protected endpoint
    me_url = '/api/v1/auth/me/'
    final_response = api_client.get(me_url)
    assert final_response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
