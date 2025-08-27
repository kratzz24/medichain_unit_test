"""
Authentication routes for signup, login, password reset, and user management
Simple version without email verification - for stable functionality
"""
from flask import Blueprint, request, jsonify
from auth.auth_utils import auth_utils
from db.supabase_client import SupabaseClient
from email_validator import validate_email, EmailNotValidError
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
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

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint using Supabase auth and profiles table"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
        missing_fields = []
        for field in required_fields:
            if not data.get(field):
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            return jsonify({'error': error_msg}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        role = data['role'].lower()
        
        # Validate email
        try:
            validate_email(email)
        except EmailNotValidError as e:
            return jsonify({'error': str(e)}), 400
        
        # Validate role
        if role not in ['doctor', 'patient', 'admin']:
            return jsonify({'error': 'Role must be doctor, patient, or admin'}), 400
        
        # Validate password
        password_error = validate_password(password)
        if password_error:
            return jsonify({'error': password_error}), 400
        
        # Step 1: Create user in Supabase Auth system
        user_id = None
        try:
            print(f"DEBUG: Attempting to create user with email: {email}")
            print(f"DEBUG: first_name value: '{first_name}'")
            print(f"DEBUG: last_name value: '{last_name}'")
            
            # Create auth user with metadata that the trigger can use
            auth_response = supabase.service_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,  # Auto-confirm for simplicity
                "user_metadata": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": role,
                    "full_name": f"{first_name} {last_name}"
                }
            })
            
            if not auth_response.user:
                return jsonify({'error': 'Failed to create user in auth system'}), 500
                
            user_id = auth_response.user.id
            print(f"DEBUG: Created user with ID: {user_id}")
            
        except Exception as auth_error:
            print(f"DEBUG: Auth creation error: {auth_error}")
            
            # Check if it's a profile constraint error
            if "null value in column" in str(auth_error) and "first_name" in str(auth_error):
                print("DEBUG: Profile creation trigger error - trying manual approach")
                return jsonify({'error': 'User creation failed due to profile constraints. Please try again.'}), 500
            
            if "already registered" in str(auth_error).lower() or "already exists" in str(auth_error).lower():
                return jsonify({'error': 'Email already registered'}), 409
            return jsonify({'error': f'Failed to create user account: {str(auth_error)}'}), 500
        
        # Step 2: Handle profile creation
        profile_data = {
            'id': user_id,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'role': role
        }
        
        try:
            # Check if profile already exists (in case trigger created it)
            existing_profile = supabase.service_client.table('profiles').select('*').eq('id', user_id).execute()
            
            if existing_profile.data:
                print(f"DEBUG: Profile already exists")
                profile = existing_profile.data[0]
            else:
                # Profile doesn't exist, create it manually
                print("DEBUG: Creating profile manually")
                profile_response = supabase.service_client.table('profiles').insert(profile_data).execute()
                
                if not profile_response.data:
                    return jsonify({'error': 'Failed to create user profile'}), 500
                    
                profile = profile_response.data[0]
                
            # Create role-specific record
            if role == 'patient':
                patient_data = {'user_id': user_id}
                supabase.service_client.table('patients').insert(patient_data).execute()
            elif role == 'doctor':
                doctor_data = {'user_id': user_id}
                supabase.service_client.table('doctors').insert(doctor_data).execute()
            
            # Generate JWT token for immediate login
            token = auth_utils.generate_token(user_id, email, role)
            
            return jsonify({
                'success': True,
                'message': 'Account created successfully!',
                'data': {
                    'user': {
                        'id': profile['id'],
                        'email': profile['email'],
                        'first_name': profile['first_name'],
                        'last_name': profile['last_name'],
                        'role': profile['role']
                    },
                    'token': token
                }
            }), 201
                
        except Exception as profile_error:
            print(f"DEBUG: Profile creation error: {profile_error}")
            # Clean up auth user if profile creation fails
            try:
                supabase.service_client.auth.admin.delete_user(user_id)
            except:
                pass
            return jsonify({'error': f'Failed to create user profile: {str(profile_error)}'}), 500
            
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint using Supabase auth"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Step 1: Authenticate with Supabase Auth
        try:
            auth_response = supabase.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.user:
                return jsonify({'error': 'Invalid email or password'}), 401
            
            user_id = auth_response.user.id
            
        except Exception as auth_error:
            print(f"Auth error: {auth_error}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Step 2: Get user profile
        profile_response = supabase.service_client.table('profiles').select('*').eq('id', user_id).execute()
        
        if not profile_response.data:
            return jsonify({'error': 'User profile not found'}), 404
        
        profile = profile_response.data[0]
        
        # Generate token
        token = auth_utils.generate_token(profile['id'], profile['email'], profile['role'])
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': {
                    'id': profile['id'],
                    'email': profile['email'],
                    'full_name': profile['full_name'],
                    'role': profile['role']
                },
                'token': token
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug log
        return jsonify({'error': 'Invalid email or password'}), 401

@auth_bp.route('/me', methods=['GET'])
@auth_utils.token_required
def get_current_user():
    """Get current user information from profiles table"""
    try:
        user_id = request.current_user['user_id']
        
        # Get user profile using service client
        profile_response = supabase.service_client.table('profiles').select('*').eq('id', user_id).execute()
        
        if not profile_response.data:
            return jsonify({'error': 'User not found'}), 404
            
        profile = profile_response.data[0]
        
        return jsonify({
            'success': True,
            'data': {
                'user': profile
            }
        }), 200
            
    except Exception as e:
        print(f"Get current user error: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500
