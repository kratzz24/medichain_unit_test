"""
Enhanced Authentication Routes with Firebase and Supabase Integration
"""
from flask import Blueprint, request, jsonify
from auth.firebase_auth import firebase_auth_service, firebase_auth_required, firebase_role_required
from db.supabase_client import SupabaseClient
import re

auth_firebase_bp = Blueprint('auth_firebase', __name__, url_prefix='/api/auth')
supabase = SupabaseClient()

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return "Password must be at least 6 characters long"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return "Password must contain at least one digit"
    return None

@auth_firebase_bp.route('/verify', methods=['POST'])
@firebase_auth_required
def verify_token():
    """Verify Firebase token and return user info with Supabase profile"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        # Get user profile from Supabase
        response = supabase.client.table('user_profiles').select('*').eq('firebase_uid', uid).execute()
        
        if response.data:
            user_profile = response.data[0]
            
            # If user is a doctor, get doctor profile too
            doctor_profile = None
            if user_profile['role'] == 'doctor':
                doc_response = supabase.client.table('doctor_profiles').select('*').eq('firebase_uid', uid).execute()
                if doc_response.data:
                    doctor_profile = doc_response.data[0]
            
            return jsonify({
                'success': True,
                'user': {
                    'uid': uid,
                    'email': firebase_user['email'],
                    'email_verified': firebase_user['email_verified'],
                    'profile': user_profile,
                    'doctor_profile': doctor_profile
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User profile not found in database'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/profile', methods=['GET'])
@firebase_auth_required
def get_profile():
    """Get user profile"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        # Get user profile from Supabase
        response = supabase.client.table('user_profiles').select('*').eq('firebase_uid', uid).execute()
        
        if response.data:
            user_profile = response.data[0]
            return jsonify({
                'success': True,
                'profile': user_profile
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/profile', methods=['PUT'])
@firebase_auth_required
def update_profile():
    """Update user profile"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Remove fields that shouldn't be updated directly
        restricted_fields = ['id', 'firebase_uid', 'created_at', 'updated_at']
        for field in restricted_fields:
            data.pop(field, None)
        
        # Update user profile in Supabase
        response = supabase.client.table('user_profiles').update(data).eq('firebase_uid', uid).execute()
        
        if response.data:
            return jsonify({
                'success': True,
                'profile': response.data[0]
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update profile'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/create-profile', methods=['POST'])
@firebase_auth_required
def create_profile():
    """Create user profile after Firebase signup"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'role']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Validate role
        valid_roles = ['patient', 'doctor', 'admin']
        if data['role'] not in valid_roles:
            return jsonify({'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'}), 400
        
        # Check if profile already exists
        existing = supabase.client.table('user_profiles').select('id').eq('firebase_uid', uid).execute()
        if existing.data:
            return jsonify({'error': 'Profile already exists'}), 409
        
        # Create profile data
        profile_data = {
            'firebase_uid': uid,
            'email': firebase_user['email'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'phone': data.get('phone'),
            'role': data['role'],
            'gender': data.get('gender'),
            'date_of_birth': data.get('date_of_birth')
        }
        
        # Insert user profile
        response = supabase.client.table('user_profiles').insert(profile_data).execute()
        
        if not response.data:
            return jsonify({'error': 'Failed to create profile'}), 500
        
        created_profile = response.data[0]
        
        # If user is a doctor, create doctor profile
        if data['role'] == 'doctor':
            doctor_data = {
                'firebase_uid': uid,
                'user_id': created_profile['id'],
                'license_number': data.get('license_number', ''),
                'specialization': data.get('specialization', ''),
                'years_of_experience': data.get('years_of_experience', 0),
                'hospital_affiliation': data.get('hospital_affiliation'),
                'consultation_fee': data.get('consultation_fee', 0),
                'bio': data.get('bio')
            }
            
            doc_response = supabase.client.table('doctor_profiles').insert(doctor_data).execute()
            
            if doc_response.data:
                created_profile['doctor_profile'] = doc_response.data[0]
        
        return jsonify({
            'success': True,
            'profile': created_profile
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/doctor-profile', methods=['GET'])
@firebase_role_required(['doctor'])
def get_doctor_profile():
    """Get doctor-specific profile"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        response = supabase.client.table('doctor_profiles').select('*').eq('firebase_uid', uid).execute()
        
        if response.data:
            return jsonify({
                'success': True,
                'doctor_profile': response.data[0]
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Doctor profile not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/doctor-profile', methods=['PUT'])
@firebase_role_required(['doctor'])
def update_doctor_profile():
    """Update doctor-specific profile"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Remove fields that shouldn't be updated directly
        restricted_fields = ['id', 'firebase_uid', 'user_id', 'created_at', 'updated_at']
        for field in restricted_fields:
            data.pop(field, None)
        
        response = supabase.client.table('doctor_profiles').update(data).eq('firebase_uid', uid).execute()
        
        if response.data:
            return jsonify({
                'success': True,
                'doctor_profile': response.data[0]
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update doctor profile'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/users', methods=['GET'])
@firebase_role_required(['admin'])
def get_all_users():
    """Get all users (admin only)"""
    try:
        response = supabase.client.table('user_profiles').select('*').execute()
        
        return jsonify({
            'success': True,
            'users': response.data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/doctors', methods=['GET'])
def get_all_doctors():
    """Get all doctors (public endpoint)"""
    try:
        response = supabase.client.table('doctor_profiles').select("""
            *,
            user_profile:user_profiles(first_name, last_name, email, phone)
        """).execute()
        
        return jsonify({
            'success': True,
            'doctors': response.data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/user/<user_id>', methods=['DELETE'])
@firebase_role_required(['admin'])
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        # Delete from Supabase (cascading will handle related tables)
        response = supabase.client.table('user_profiles').delete().eq('firebase_uid', user_id).execute()
        
        if response.data:
            # Also delete from Firebase
            firebase_result = firebase_auth_service.delete_user(user_id)
            
            return jsonify({
                'success': True,
                'firebase_deletion': firebase_result['success']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
