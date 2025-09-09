"""
Shared test fixtures and configuration
"""
import pytest
import os
import sys
from unittest.mock import Mock

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing"""
    mock_client = Mock()
    mock_service_client = Mock()

    # Set up common mock responses
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(data=[])
    mock_service_client.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(data=[])

    return {
        'client': mock_client,
        'service_client': mock_service_client
    }


@pytest.fixture
def sample_user_profile():
    """Sample user profile data for testing"""
    return {
        'id': 'test-user-id',
        'firebase_uid': 'test-firebase-uid',
        'email': 'test@example.com',
        'first_name': 'John',
        'last_name': 'Doe',
        'role': 'patient'
    }


@pytest.fixture
def sample_doctor_profile():
    """Sample doctor profile data for testing"""
    return {
        'id': 'test-doctor-id',
        'firebase_uid': 'test-firebase-uid',
        'user_id': 'test-user-id',
        'license_number': 'DOC12345',
        'specialization': 'Cardiology',
        'years_of_experience': 10
    }


@pytest.fixture
def mock_firebase_token():
    """Mock Firebase ID token data"""
    return {
        'success': True,
        'uid': 'test-firebase-uid',
        'email': 'test@example.com',
        'email_verified': True,
        'name': 'John Doe'
    }
