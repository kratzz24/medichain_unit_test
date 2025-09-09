"""
Tests for Firebase authentication routes
"""
import pytest
import json
from unittest.mock import Mock, patch
from app import app
from auth.firebase_auth import firebase_auth_service


@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_firebase_auth():
    """Mock Firebase authentication service"""
    with patch('auth.firebase_auth.firebase_auth_service') as mock_auth:
        mock_auth.verify_token.return_value = {
            'success': True,
            'uid': 'test-uid-123',
            'email': 'test@example.com',
            'email_verified': True
        }
        yield mock_auth


class TestAuthRoutes:
    """Test cases for authentication routes"""

    def test_verify_token_success(self, client, mock_firebase_auth):
        """Test successful token verification"""
        # Mock the database response
        with patch('auth.firebase_auth_routes.supabase') as mock_supabase:
            mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
                data=[{
                    'id': '1',
                    'firebase_uid': 'test-uid-123',
                    'email': 'test@example.com',
                    'role': 'patient',
                    'first_name': 'John',
                    'last_name': 'Doe'
                }]
            )

            response = client.post('/api/auth/verify',
                                 headers={'Authorization': 'Bearer test-token'})

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['user']['uid'] == 'test-uid-123'

    def test_verify_token_no_profile(self, client, mock_firebase_auth):
        """Test token verification when no user profile exists"""
        with patch('auth.firebase_auth_routes.supabase') as mock_supabase:
            mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
                data=[]
            )

            response = client.post('/api/auth/verify',
                                 headers={'Authorization': 'Bearer test-token'})

            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False

    def test_login_success(self, client):
        """Test successful login"""
        with patch('auth.firebase_auth_routes.firebase_auth_service') as mock_auth, \
             patch('auth.firebase_auth_routes.supabase') as mock_supabase:

            # Mock token verification
            mock_auth.verify_token.return_value = {
                'success': True,
                'uid': 'test-uid-123',
                'email': 'test@example.com',
                'email_verified': True
            }

            # Mock database response
            mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
                data=[{
                    'id': '1',
                    'firebase_uid': 'test-uid-123',
                    'email': 'test@example.com',
                    'role': 'patient',
                    'first_name': 'John',
                    'last_name': 'Doe'
                }]
            )

            response = client.post('/api/auth/login',
                                 json={'id_token': 'test-token'})

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['user']['uid'] == 'test-uid-123'

    def test_login_missing_token(self, client):
        """Test login with missing ID token"""
        response = client.post('/api/auth/login', json={})

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'ID token is required' in data['error']

    def test_login_invalid_token(self, client):
        """Test login with invalid token"""
        with patch('auth.firebase_auth_routes.firebase_auth_service') as mock_auth:
            mock_auth.verify_token.return_value = {
                'success': False,
                'error': 'Invalid token'
            }

            response = client.post('/api/auth/login',
                                 json={'id_token': 'invalid-token'})

            assert response.status_code == 401
            data = json.loads(response.data)
            assert data['success'] is False


if __name__ == '__main__':
    pytest.main([__file__])
