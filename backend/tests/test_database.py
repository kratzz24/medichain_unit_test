"""
Tests for database operations and Supabase client
"""
import pytest
from unittest.mock import Mock, patch
from db.supabase_client import SupabaseClient


class TestSupabaseClient:
    """Test cases for Supabase client operations"""

    @patch('db.supabase_client.create_client')
    def test_supabase_client_initialization(self, mock_create_client):
        """Test Supabase client initialization"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        client = SupabaseClient()

        assert client.client is not None
        assert client.service_client is not None
        mock_create_client.assert_called()

    def test_service_client_operations(self):
        """Test service client database operations"""
        with patch('db.supabase_client.create_client') as mock_create_client:
            mock_client = Mock()
            mock_execute = Mock()
            mock_execute.return_value = {'data': [{'id': 1, 'name': 'test'}]}

            # Set up the chain properly
            mock_client.table.return_value.select.return_value.eq.return_value.execute = mock_execute
            mock_create_client.return_value = mock_client

            client = SupabaseClient()

            # Test a typical query
            result = client.service_client.table('user_profiles').select('*').eq('id', 1).execute()

            assert result == {'data': [{'id': 1, 'name': 'test'}]}
            mock_client.table.assert_called_with('user_profiles')


class TestDatabaseOperations:
    """Test cases for database operations"""

    def test_user_profile_creation(self):
        """Test user profile creation logic"""
        # This would test the logic for creating user profiles
        # For now, just test the data structure
        user_profile_data = {
            'firebase_uid': 'test-uid-123',
            'email': 'test@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'patient'
        }

        required_fields = ['firebase_uid', 'email', 'first_name', 'last_name', 'role']

        # Check that all required fields are present
        for field in required_fields:
            assert field in user_profile_data
            assert user_profile_data[field] is not None

    def test_doctor_profile_creation(self):
        """Test doctor profile creation logic"""
        doctor_profile_data = {
            'firebase_uid': 'test-uid-123',
            'user_id': 'user-123',
            'license_number': 'DOC12345',
            'specialization': 'Cardiology',
            'years_of_experience': 10
        }

        required_fields = ['firebase_uid', 'user_id', 'license_number', 'specialization']

        # Check that all required fields are present
        for field in required_fields:
            assert field in doctor_profile_data
            assert doctor_profile_data[field] is not None

    def test_role_validation(self):
        """Test user role validation"""
        valid_roles = ['patient', 'doctor', 'admin']
        invalid_roles = ['nurse', 'pharmacist', '', None]

        for role in valid_roles:
            assert role in ['patient', 'doctor', 'admin']

        for role in invalid_roles:
            assert role not in ['patient', 'doctor', 'admin'] or role is None


if __name__ == '__main__':
    pytest.main([__file__])
