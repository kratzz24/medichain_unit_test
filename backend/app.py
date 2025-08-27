"""
Flask backend application for medical records with AES encryption and SHA-256 hashing
"""
# Disable SSL verification BEFORE importing anything (Windows SSL issues)
import os
import ssl
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['SSL_VERIFY'] = 'false'

# Set SSL context globally to not verify certificates
ssl._create_default_https_context = ssl._create_unverified_context

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from core.crypto_utils import MedicalRecordCrypto
from db.supabase_client import SupabaseClient
from datetime import datetime
from auth.auth_routes_simple import auth_bp

# Import our custom AI system
try:
    from medichain_ai import MediChainAI
    ai_system = MediChainAI()
except Exception as e:
    ai_system = None

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize services
supabase_client = SupabaseClient()
crypto = MedicalRecordCrypto(os.getenv('AES_ENCRYPTION_KEY', '').encode('utf-8'))

# Register blueprints
app.register_blueprint(auth_bp)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'medical-records-api'})

# ========================================
# AI DIAGNOSIS ENDPOINTS - CUSTOM AI SYSTEM
# ========================================

@app.route('/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint that matches frontend expectations
    This is the endpoint your React frontend calls
    """
    try:
        if not ai_system:
            return jsonify({'error': 'AI system not available'}), 503
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract symptoms from the request data
        symptoms_text = data.get('symptoms', '') or data.get('chief_complaint', '')
        
        if not symptoms_text:
            return jsonify({'error': 'Symptoms required'}), 400
        
        # Get AI diagnosis
        result = ai_system.diagnose(user_input=symptoms_text)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        # Transform to match frontend expectations exactly
        response = {
            'status': 'success',
            'analysis': {
                'primary_diagnosis': {
                    'condition': result['primary_diagnosis'],
                    'confidence': result['confidence_raw'],
                    'explanation': f"Diagnosed based on symptom analysis with {result['confidence']}% confidence",
                    'description': f"{result['primary_diagnosis']} - {result['severity']} severity case"
                },
                'differential_diagnoses': [alt['diagnosis'] for alt in result['alternative_diagnoses'][1:4]],
                'severity': result['severity'],
                'confidence_score': result['confidence_raw']
            },
            'recommendations': {
                'medications': result['prescriptions'],
                'treatments': [result['prescriptions'][0]['medication']] if result['prescriptions'] else [],
                'immediate_actions': [result['recommendations']['immediate_care']],
                'lifestyle_advice': [
                    result['recommendations']['follow_up'],
                    "Rest and stay hydrated",
                    "Monitor symptoms closely"
                ],
                'warnings': result['recommendations']['emergency_signs'][:3],  # Top 3 warnings
                'follow_up': result['recommendations']['follow_up']
            },
            'next_steps': {
                'urgency_level': result['severity'],
                'immediate_actions': result['severity'] in ['Severe', 'Critical'],
                'follow_up_days': 3 if result['severity'] == 'Mild' else (1 if result['severity'] == 'Severe' else 2)
            },
            'ai_model_version': result['ai_system'],
            'timestamp': str(datetime.now()),
            'medical_disclaimer': 'This AI diagnosis is for informational purposes only. Please consult with a healthcare professional for proper medical advice.',
            'metadata': {
                'detected_symptoms': result['detected_symptoms'],
                'severity_score': result['severity_score'],
                'active_symptoms': result['active_symptoms']
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'AI diagnosis failed: {str(e)}'}), 500

@app.route('/api/ai/diagnose', methods=['POST'])
def ai_diagnose():
    """
    Enhanced AI Diagnosis endpoint using our custom MediChain AI
    Supports both guest and authenticated users with optional data saving
    """
    try:
        if not ai_system:
            return jsonify({
                'success': False,
                'error': 'AI system not available'
            }), 503
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract data from request
        symptoms_text = data.get('symptoms', '')
        patient_data = data.get('patient_data', {})
        save_to_database = data.get('save_to_database', False)
        session_type = data.get('session_type', 'guest')  # 'guest' or 'authenticated'
        
        if not symptoms_text:
            return jsonify({
                'success': False,
                'error': 'Symptoms are required'
            }), 400
        
        # Get AI diagnosis
        result = ai_system.diagnose(user_input=symptoms_text)
        
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
        # Create response in expected format
        diagnosis_response = {
            'diagnosis': result['primary_diagnosis'],
            'confidence': result['confidence_raw'],
            'prescription': result['prescriptions'][0]['medication'] if result['prescriptions'] else 'No prescription recommended',
            'recommendations': result['recommendations']['immediate_care'],
            'severity': result['severity'],
            'session_id': f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'session_type': session_type,
            'timestamp': datetime.now().isoformat(),
            'alternative_diagnoses': result['alternative_diagnoses'][:3],
            'detected_symptoms': result['detected_symptoms'],
            'medical_disclaimer': 'This AI diagnosis is for informational purposes only. Please consult with a healthcare professional for proper medical advice.'
        }
        
        # Save to database if requested and user is authenticated
        if save_to_database and session_type == 'authenticated' and patient_data.get('patient_id'):
            try:
                # Create consultation record
                consultation_data = {
                    'patient_id': patient_data.get('patient_id'),
                    'symptoms': symptoms_text,
                    'patient_age': patient_data.get('age'),
                    'patient_gender': patient_data.get('gender'),
                    'ai_diagnosis': result['primary_diagnosis'],
                    'confidence_score': result['confidence_raw'],
                    'ai_prescription': result['prescriptions'][0]['medication'] if result['prescriptions'] else None,
                    'ai_recommendations': result['recommendations']['immediate_care'],
                    'session_id': diagnosis_response['session_id'],
                    'session_type': session_type,
                    'created_at': datetime.now().isoformat(),
                    'doctor_review': None,
                    'doctor_notes': None,
                    'modified_prescription': None
                }
                
                # Here you would save to your database
                # For now, we'll just log that it would be saved
                print(f"Would save consultation data for patient {patient_data.get('patient_id')}")
                diagnosis_response['saved_to_database'] = True
                
            except Exception as e:
                print(f"Failed to save consultation: {str(e)}")
                diagnosis_response['saved_to_database'] = False
        else:
            diagnosis_response['saved_to_database'] = False
        
        return jsonify({
            'success': True,
            'data': diagnosis_response
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'AI diagnosis failed: {str(e)}'
        }), 500

@app.route('/api/ai/patient-history/<patient_id>', methods=['GET'])
def get_patient_ai_history(patient_id):
    """
    Get AI consultation history for a specific patient (for doctors)
    """
    try:
        # In a real implementation, you would:
        # 1. Verify the requesting user is a doctor
        # 2. Verify the doctor has permission to view this patient's data
        # 3. Fetch consultation history from database
        
        # For now, return mock data
        mock_history = [
            {
                'id': f'consult_1_{patient_id}',
                'patient_id': patient_id,
                'timestamp': '2024-01-15T10:30:00Z',
                'symptoms': 'Persistent headache, fatigue, difficulty concentrating',
                'patient_age': 35,
                'patient_gender': 'female',
                'ai_diagnosis': 'Tension-type headache possibly related to stress',
                'confidence_score': 85,
                'ai_prescription': 'Ibuprofen 400mg every 6-8 hours, stress management techniques',
                'ai_recommendations': 'Ensure adequate sleep, stay hydrated, consider stress reduction activities',
                'session_id': 'session_20240115_1030',
                'session_type': 'authenticated',
                'doctor_review': None,
                'doctor_notes': None,
                'modified_prescription': None,
                'created_at': '2024-01-15T10:30:00Z'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'patient_id': patient_id,
                'consultations': mock_history,
                'total_count': len(mock_history)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get patient history: {str(e)}'
        }), 500

@app.route('/api/ai/doctor-review', methods=['POST'])
def submit_doctor_review():
    """
    Submit doctor review for an AI consultation
    """
    try:
        data = request.get_json()
        
        consultation_id = data.get('consultation_id')
        doctor_notes = data.get('doctor_notes')
        modified_prescription = data.get('modified_prescription')
        doctor_id = data.get('doctor_id')
        
        if not consultation_id or not doctor_notes:
            return jsonify({
                'success': False,
                'error': 'Consultation ID and doctor notes are required'
            }), 400
        
        # In a real implementation, you would:
        # 1. Verify the doctor has permission to review this consultation
        # 2. Update the consultation record in the database
        # 3. Log the review activity
        
        # For now, just return success
        review_data = {
            'consultation_id': consultation_id,
            'doctor_id': doctor_id,
            'doctor_notes': doctor_notes,
            'modified_prescription': modified_prescription,
            'reviewed_at': datetime.now().isoformat(),
            'status': 'reviewed'
        }
        
        return jsonify({
            'success': True,
            'data': review_data,
            'message': 'Doctor review submitted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to submit review: {str(e)}'
        }), 500

@app.route('/api/patients/list', methods=['GET'])
def get_patients_list():
    """
    Get list of patients for doctor dashboard
    """
    try:
        # In a real implementation, you would:
        # 1. Verify the requesting user is a doctor
        # 2. Fetch patients assigned to this doctor from database
        
        # For now, return mock data
        mock_patients = [
            {
                'id': '1',
                'name': 'John Doe',
                'email': 'john@example.com',
                'age': 35,
                'gender': 'male',
                'last_consultation': '2024-01-15T10:30:00Z',
                'total_consultations': 3,
                'pending_reviews': 1
            },
            {
                'id': '2',
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'age': 28,
                'gender': 'female',
                'last_consultation': '2024-01-14T14:15:00Z',
                'total_consultations': 2,
                'pending_reviews': 0
            }
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'patients': mock_patients,
                'total_count': len(mock_patients)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get patients list: {str(e)}'
        }), 500
def ai_system_info():
    """Get information about our custom AI system"""
    try:
        if not ai_system:
            return jsonify({'error': 'AI system not available'}), 503
        
        info = ai_system.get_system_info()
        return jsonify({
            'success': True,
            'system_info': info
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get system info: {str(e)}'}), 500

@app.route('/api/ai/quick-diagnosis', methods=['POST'])
def quick_diagnosis():
    """
    Quick AI diagnosis for simple symptom checking
    Returns just the primary diagnosis and prescription
    """
    try:
        if not ai_system:
            return jsonify({'error': 'AI system not available'}), 503
        
        data = request.get_json()
        symptoms_text = data.get('symptoms', '')
        
        if not symptoms_text:
            return jsonify({'error': 'Symptoms text required'}), 400
        
        result = ai_system.diagnose(user_input=symptoms_text)
        
        if 'error' in result:
            return jsonify(result), 400
        
        # Return simplified response for quick diagnosis
        simplified_result = {
            'diagnosis': result['primary_diagnosis'],
            'confidence': result['confidence'],
            'severity': result['severity'],
            'prescription': result['prescriptions'][0] if result['prescriptions'] else None,
            'immediate_care': result['recommendations']['immediate_care']
        }
        
        return jsonify({
            'success': True,
            'result': simplified_result
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Quick diagnosis failed: {str(e)}'}), 500

@app.route('/api/medical-records', methods=['POST'])
def create_medical_record():
    """Create a new encrypted medical record"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['patient_id', 'diagnosis', 'prescription']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Encrypt sensitive fields
        encrypted_data = crypto.encrypt_medical_record(
            diagnosis=data['diagnosis'],
            prescription=data['prescription']
        )
        
        # Compute hash of encrypted data for integrity verification
        combined_encrypted = encrypted_data['diagnosis'] + encrypted_data['prescription']
        blockchain_hash = crypto.compute_hash(combined_encrypted)
        
        # Prepare record data
        record_data = {
            'patient_id': data['patient_id'],
            'doctor_id': data.get('doctor_id'),
            'diagnosis': encrypted_data['diagnosis'],
            'prescription': encrypted_data['prescription'],
            'blockchain_tx_hash': blockchain_hash
        }
        
        # Save to database
        created_record = supabase_client.create_health_record(record_data)
        
        if created_record:
            return jsonify({
                'success': True,
                'data': {
                    'id': created_record['id'],
                    'patient_id': created_record['patient_id'],
                    'doctor_id': created_record.get('doctor_id'),
                    'blockchain_tx_hash': created_record['blockchain_tx_hash'],
                    'created_at': created_record['created_at']
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to create medical record'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/medical-records/<record_id>', methods=['GET'])
def get_medical_record(record_id):
    """Retrieve and decrypt a medical record"""
    try:
        record = supabase_client.get_health_record(record_id)
        
        if not record:
            return jsonify({'error': 'Medical record not found'}), 404
        
        # Decrypt sensitive fields
        decrypted_data = crypto.decrypt_medical_record(
            encrypted_diagnosis=record['diagnosis'],
            encrypted_prescription=record['prescription']
        )
        
        # Verify integrity
        combined_encrypted = record['diagnosis'] + record['prescription']
        computed_hash = crypto.compute_hash(combined_encrypted)
        is_valid = computed_hash == record['blockchain_tx_hash']
        
        return jsonify({
            'success': True,
            'data': {
                'id': record['id'],
                'patient_id': record['patient_id'],
                'doctor_id': record.get('doctor_id'),
                'diagnosis': decrypted_data['diagnosis'],
                'prescription': decrypted_data['prescription'],
                'blockchain_tx_hash': record['blockchain_tx_hash'],
                'is_integrity_valid': is_valid,
                'created_at': record['created_at']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/medical-records/patient/<patient_id>', methods=['GET'])
def get_patient_medical_records(patient_id):
    """Get all medical records for a specific patient"""
    try:
        records = supabase_client.get_health_records_by_patient(patient_id)
        
        decrypted_records = []
        for record in records:
            decrypted_data = crypto.decrypt_medical_record(
                encrypted_diagnosis=record['diagnosis'],
                encrypted_prescription=record['prescription']
            )
            
            combined_encrypted = record['diagnosis'] + record['prescription']
            computed_hash = crypto.compute_hash(combined_encrypted)
            is_valid = computed_hash == record['blockchain_tx_hash']
            
            decrypted_records.append({
                'id': record['id'],
                'patient_id': record['patient_id'],
                'doctor_id': record.get('doctor_id'),
                'diagnosis': decrypted_data['diagnosis'],
                'prescription': decrypted_data['prescription'],
                'blockchain_tx_hash': record['blockchain_tx_hash'],
                'is_integrity_valid': is_valid,
                'created_at': record['created_at']
            })
        
        return jsonify({
            'success': True,
            'data': decrypted_records
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/medical-records/<record_id>', methods=['PUT'])
def update_medical_record(record_id):
    """Update an existing medical record"""
    try:
        data = request.get_json()
        
        # Get existing record
        existing_record = supabase_client.get_health_record(record_id)
        if not existing_record:
            return jsonify({'error': 'Medical record not found'}), 404
        
        # Encrypt updated fields
        encrypted_data = {}
        if 'diagnosis' in data:
            encrypted_data['diagnosis'] = crypto.encrypt_field(data['diagnosis'])
        else:
            encrypted_data['diagnosis'] = existing_record['diagnosis']
            
        if 'prescription' in data:
            encrypted_data['prescription'] = crypto.encrypt_field(data['prescription'])
        else:
            encrypted_data['prescription'] = existing_record['prescription']
        
        # Update hash
        combined_encrypted = encrypted_data['diagnosis'] + encrypted_data['prescription']
        encrypted_data['blockchain_tx_hash'] = crypto.compute_hash(combined_encrypted)
        
        # Update record
        updated_record = supabase_client.update_health_record(record_id, encrypted_data)
        
        if updated_record:
            return jsonify({
                'success': True,
                'data': {
                    'id': updated_record['id'],
                    'patient_id': updated_record['patient_id'],
                    'doctor_id': updated_record.get('doctor_id'),
                    'blockchain_tx_hash': updated_record['blockchain_tx_hash'],
                    'created_at': updated_record['created_at']
                }
            }), 200
        else:
            return jsonify({'error': 'Failed to update medical record'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/medical-records/<record_id>', methods=['DELETE'])
def delete_medical_record(record_id):
    """Delete a medical record"""
    try:
        deleted_record = supabase_client.delete_health_record(record_id)
        
        if deleted_record:
            return jsonify({'success': True, 'message': 'Medical record deleted'}), 200
        else:
            return jsonify({'error': 'Medical record not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('FLASK_PORT', 5000)))
