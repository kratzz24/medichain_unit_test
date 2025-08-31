from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
import os
import logging
from symptom_parser import SymptomParser  # Import our new symptom parser
from enhanced_medical_recommendations import get_enhanced_medical_recommendations  # Import enhanced recommendations
from conversational_medical_guide import conversational_guide  # Import conversational guide

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load model and encoders - Using enhanced comprehensive model
MODEL_PATH = 'enhanced_diagnosis_model.pkl'  # Enhanced model with 56 diagnoses
LABEL_ENCODER_PATH = 'enhanced_label_encoder.pkl'
FEATURE_NAMES_PATH = 'enhanced_feature_names.pkl'
PRESCRIPTIONS_PATH = 'enhanced_prescriptions_map.pkl'  # Enhanced prescriptions map

# Global variables for model and encoders
model = None
label_encoder = None
feature_names = None
prescriptions_map = None  # Enhanced prescriptions map
symptom_parser = None  # Will hold our symptom parser instance

def load_model():
    """Load the trained model and encoders"""
    global model, label_encoder, feature_names, prescriptions_map, symptom_parser
    
    try:
        # Load enhanced model
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            logger.info(f"Enhanced model loaded successfully from {MODEL_PATH}")
        else:
            logger.error(f"Enhanced model file not found: {MODEL_PATH}")
            return False
            
        # Load enhanced label encoder
        if os.path.exists(LABEL_ENCODER_PATH):
            label_encoder = joblib.load(LABEL_ENCODER_PATH)
            logger.info(f"Enhanced label encoder loaded successfully from {LABEL_ENCODER_PATH}")
        else:
            logger.error(f"Enhanced label encoder file not found: {LABEL_ENCODER_PATH}")
            return False
            
        # Load enhanced feature names
        if os.path.exists(FEATURE_NAMES_PATH):
            feature_names = joblib.load(FEATURE_NAMES_PATH)
            logger.info(f"Enhanced feature names loaded successfully from {FEATURE_NAMES_PATH}")
        else:
            logger.error(f"Enhanced feature names file not found: {FEATURE_NAMES_PATH}")
            return False
            
        # Load enhanced prescriptions map
        if os.path.exists(PRESCRIPTIONS_PATH):
            prescriptions_map = joblib.load(PRESCRIPTIONS_PATH)
            logger.info(f"Enhanced prescriptions map loaded successfully from {PRESCRIPTIONS_PATH}")
            logger.info(f"Loaded {len(prescriptions_map)} diagnosis prescriptions")
        else:
            logger.warning(f"Enhanced prescriptions map not found: {PRESCRIPTIONS_PATH}")
            prescriptions_map = {}
        
        # Initialize our custom symptom parser with the current directory
        symptom_parser = SymptomParser(model_path=".")
        logger.info(f"Symptom parser initialized with {len(feature_names)} features")
        logger.info(f"Total diagnoses available: {len(label_encoder.classes_)}")
            
        return True
        
    except Exception as e:
        logger.error(f"Error loading enhanced model: {str(e)}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'label_encoder_loaded': label_encoder is not None,
        'feature_names_loaded': feature_names is not None,
        'prescriptions_loaded': prescriptions_map is not None,
        'total_diagnoses': len(label_encoder.classes_) if label_encoder else 0,
        'model_type': 'enhanced_comprehensive'
    })

@app.route('/chat', methods=['POST'])
def conversational_diagnosis():
    """Conversational AI diagnosis endpoint - returns natural language response"""
    if model is None or label_encoder is None or feature_names is None or symptom_parser is None:
        return jsonify({'error': 'Model or symptom parser not loaded'}), 500
    
    try:
        data = request.get_json()
        logger.info(f"Received conversational request: {data}")
        
        if not data or 'symptoms' not in data:
            return jsonify({'error': 'No symptoms provided'}), 400
        
        symptoms = data['symptoms']
        response_type = data.get('response_type', 'general')  # 'general' or 'medication'
        
        # Process symptoms using the same logic as predict endpoint
        if isinstance(symptoms, dict) and 'symptomText' in symptoms:
            symptom_text = symptoms['symptomText']
            feature_vector = symptom_parser.get_feature_vector(symptom_text)
            processed_symptoms = symptom_parser.parse_symptoms(symptom_text)
        else:
            return jsonify({'error': 'Symptoms must contain symptomText field'}), 400
            
        # Make prediction
        features = np.array([feature_vector])
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        # Get diagnosis name
        diagnosis = label_encoder.inverse_transform([prediction])[0]
        
        # Get top predictions
        n_classes = len(label_encoder.classes_)
        top_n = min(3, n_classes)
        top_indices = np.argsort(probabilities)[-top_n:][::-1]
        top_diagnoses = label_encoder.inverse_transform(top_indices)
        top_probabilities = probabilities[top_indices]
        
        # Get medical recommendations
        medical_recommendations = get_enhanced_medical_recommendations(diagnosis)
        
        # Apply confidence boosting
        base_confidence = float(probabilities[prediction])
        symptom_strength = np.sum(feature_vector) / len(feature_vector)
        confidence_boost = min(0.3, symptom_strength * 0.2)
        
        if 'confidence_boost' in medical_recommendations:
            enhanced_confidence = medical_recommendations['confidence_boost'] / 100.0
        else:
            enhanced_confidence = min(0.95, base_confidence + confidence_boost)
        
        # Create alternative diagnoses list
        boosted_top_3 = []
        for diag, prob in zip(top_diagnoses, top_probabilities):
            diag_recommendations = get_enhanced_medical_recommendations(diag)
            if 'confidence_boost' in diag_recommendations:
                boosted_prob = min(0.95, diag_recommendations['confidence_boost'] / 100.0)
            else:
                boosted_prob = min(0.95, float(prob) + confidence_boost)
            
            boosted_top_3.append({
                'diagnosis': diag,
                'confidence': boosted_prob
            })
        
        # Generate appropriate conversational response
        if response_type == 'medication':
            conversational_text = conversational_guide.generate_medication_focused_response(
                diagnosis=diagnosis,
                symptoms_text=symptom_text,
                medical_recommendations=medical_recommendations
            )
        else:
            conversational_text = conversational_guide.generate_conversational_response(
                diagnosis=diagnosis,
                confidence=enhanced_confidence * 100,
                symptoms_text=symptom_text,
                medical_recommendations=medical_recommendations,
                alternative_diagnoses=boosted_top_3
            )
        
        response = {
            'conversational_response': conversational_text,
            'diagnosis': diagnosis,
            'confidence': enhanced_confidence * 100,
            'alternative_diagnoses': boosted_top_3,
            'response_type': response_type
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in conversational diagnosis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/symptoms', methods=['GET'])
def get_symptoms():
    """Get list of available symptoms"""
    if feature_names is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    return jsonify({'symptoms': feature_names})

@app.route('/diagnoses', methods=['GET'])
def get_diagnoses():
    """Get list of available diagnoses"""
    if label_encoder is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    diagnoses = label_encoder.classes_.tolist()
    return jsonify({'diagnoses': diagnoses})

@app.route('/predict', methods=['POST'])
def predict_diagnosis():
    """Predict diagnosis based on symptoms"""
    if model is None or label_encoder is None or feature_names is None or symptom_parser is None:
        return jsonify({'error': 'Model or symptom parser not loaded'}), 500
    
    try:
        data = request.get_json()
        logger.info(f"Received prediction request: {data}")
        
        if not data or 'symptoms' not in data:
            return jsonify({'error': 'No symptoms provided'}), 400
        
        symptoms = data['symptoms']
        logger.info(f"Symptoms data type: {type(symptoms)}, content: {symptoms}")
        
        # Process the symptoms based on the format received
        feature_vector = []
        
        # Case 1: If symptoms contains symptomText key (natural language text)
        if isinstance(symptoms, dict) and 'symptomText' in symptoms:
            symptom_text = symptoms['symptomText']
            logger.info(f"Processing symptom text: {symptom_text}")
            
            # Use our new SymptomParser to get the feature vector
            feature_vector = symptom_parser.get_feature_vector(symptom_text)
            
            # Also get the symptom dictionary for response
            processed_symptoms = symptom_parser.parse_symptoms(symptom_text)
            logger.info(f"Parsed symptoms: {processed_symptoms}")
            
        # Case 2: If symptoms is already a dictionary of feature values
        elif isinstance(symptoms, dict):
            processed_symptoms = {}
            # Initialize with zeros then add provided values
            for feature in feature_names:
                processed_symptoms[feature] = 0
                
            # Copy over any matching features
            for feature, value in symptoms.items():
                if feature in feature_names:
                    try:
                        processed_symptoms[feature] = float(value)
                    except (ValueError, TypeError):
                        return jsonify({'error': f'Invalid value for symptom {feature}'}), 400
            
            # Create feature vector in the right order
            feature_vector = [processed_symptoms.get(feature, 0.0) for feature in feature_names]
        
        else:
            return jsonify({'error': 'Symptoms must be a dictionary'}), 400
            
        logger.info(f"Feature vector (len={len(feature_vector)}): {feature_vector}")
        
        # Ensure we have the right number of features
        if len(feature_vector) != len(feature_names):
            error_msg = f"Feature vector length ({len(feature_vector)}) doesn't match feature names length ({len(feature_names)})"
            logger.error(error_msg)
            return jsonify({'error': error_msg}), 400
            
        # Create the feature array for prediction
        features = np.array([feature_vector])
        logger.info(f"Feature array shape: {features.shape}")
            
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        # Get diagnosis name
        diagnosis = label_encoder.inverse_transform([prediction])[0]
        logger.info(f"Predicted diagnosis: {diagnosis}")
        
        # Get top 3 predictions with probabilities (safely)
        # Make sure we only get as many indices as we have classes
        n_classes = len(label_encoder.classes_)
        top_n = min(3, n_classes)
        top_indices = np.argsort(probabilities)[-top_n:][::-1]
        top_diagnoses = label_encoder.inverse_transform(top_indices)
        top_probabilities = probabilities[top_indices]
        
        logger.info(f"Top diagnoses: {list(zip(top_diagnoses, top_probabilities))}")
        
        # Get enhanced medical recommendations
        medical_recommendations = get_enhanced_medical_recommendations(diagnosis)
        
        # Apply confidence boosting
        base_confidence = float(probabilities[prediction])
        
        # Boost confidence based on symptom pattern strength
        symptom_strength = np.sum(feature_vector) / len(feature_vector)
        confidence_boost = min(0.3, symptom_strength * 0.2)  # Up to 30% boost
        
        # Apply confidence boost from medical recommendations if available
        if 'confidence_boost' in medical_recommendations:
            # Use the medical knowledge confidence boost
            enhanced_confidence = medical_recommendations['confidence_boost'] / 100.0
        else:
            # Apply algorithmic confidence boost
            enhanced_confidence = min(0.95, base_confidence + confidence_boost)
        
        # Boost top 3 predictions as well
        boosted_top_3 = []
        for diag, prob in zip(top_diagnoses, top_probabilities):
            diag_recommendations = get_enhanced_medical_recommendations(diag)
            if 'confidence_boost' in diag_recommendations:
                boosted_prob = min(0.95, diag_recommendations['confidence_boost'] / 100.0)
            else:
                boosted_prob = min(0.95, float(prob) + confidence_boost)
            
            boosted_top_3.append({
                'diagnosis': diag,
                'confidence': boosted_prob
            })
        
        # Generate conversational response
        symptoms_input = symptoms.get('symptomText', '') if isinstance(symptoms, dict) else str(symptoms)
        conversational_response = conversational_guide.generate_conversational_response(
            diagnosis=diagnosis,
            confidence=enhanced_confidence * 100,  # Convert to percentage
            symptoms_text=symptoms_input,
            medical_recommendations=medical_recommendations,
            alternative_diagnoses=boosted_top_3
        )
        
        # Generate medication-focused response as well
        medication_response = conversational_guide.generate_medication_focused_response(
            diagnosis=diagnosis,
            symptoms_text=symptoms_input,
            medical_recommendations=medical_recommendations
        )
        
        # Create enhanced response
        response = {
            'diagnosis': diagnosis,
            'confidence': enhanced_confidence,
            'confidence_percentage': enhanced_confidence * 100,
            'conversational_response': conversational_response,
            'medication_response': medication_response,
            'top_3_predictions': boosted_top_3,
            'input_symptoms': symptoms,
            'medical_recommendations': medical_recommendations,
            'otc_medications': medical_recommendations.get('otc_medications', []),
            'prescription_medications': medical_recommendations.get('prescription_medications', []),
            'treatments': medical_recommendations.get('treatments', []),
            'seek_doctor': medical_recommendations.get('seek_doctor', 'Consult healthcare provider if symptoms persist'),
            'severity': medical_recommendations.get('severity', 'Moderate'),
            'estimated_duration': medical_recommendations.get('typical_duration', 'Varies')
        }
        
        logger.info(f"Enhanced prediction made: {diagnosis} (base confidence: {base_confidence:.2%}, enhanced: {enhanced_confidence:.2%})")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Predict diagnoses for multiple cases"""
    if model is None or label_encoder is None or feature_names is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.get_json()
        
        if not data or 'cases' not in data:
            return jsonify({'error': 'No cases provided'}), 400
        
        cases = data['cases']
        
        if not isinstance(cases, list):
            return jsonify({'error': 'Cases must be a list'}), 400
        
        results = []
        
        for case in cases:
            if not isinstance(case, dict) or 'symptoms' not in case:
                results.append({'error': 'Invalid case format'})
                continue
            
            symptoms = case['symptoms']
            
            # Create feature vector
            feature_vector = []
            for feature in feature_names:
                value = symptoms.get(feature, 0)
                feature_vector.append(float(value))
            
            # Make prediction
            features = np.array([feature_vector])
            prediction = model.predict(features)[0]
            probabilities = model.predict_proba(features)[0]
            
            # Get diagnosis name
            diagnosis = label_encoder.inverse_transform([prediction])[0]
            
            results.append({
                'diagnosis': diagnosis,
                'confidence': float(probabilities[prediction]),
                'case_id': case.get('id', len(results))
            })
        
        return jsonify({'results': results})
        
    except Exception as e:
        logger.error(f"Error in batch prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Load model before starting server
    if load_model():
        logger.info("Starting AI diagnosis server...")
        app.run(host='0.0.0.0', port=5001, debug=False)
    else:
        logger.error("Failed to load model. Please train the model first.")
        exit(1)
