from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load model and encoders
MODEL_PATH = 'diagnosis_model.pkl'
LABEL_ENCODER_PATH = 'label_encoder.pkl'
FEATURE_NAMES_PATH = 'feature_names.pkl'

# Global variables for model and encoders
model = None
label_encoder = None
feature_names = None

def load_model():
    """Load the trained model and encoders"""
    global model, label_encoder, feature_names
    
    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            logger.info("Model loaded successfully")
        else:
            logger.error(f"Model file not found: {MODEL_PATH}")
            return False
            
        if os.path.exists(LABEL_ENCODER_PATH):
            label_encoder = joblib.load(LABEL_ENCODER_PATH)
            logger.info("Label encoder loaded successfully")
        else:
            logger.error(f"Label encoder file not found: {LABEL_ENCODER_PATH}")
            return False
            
        if os.path.exists(FEATURE_NAMES_PATH):
            feature_names = joblib.load(FEATURE_NAMES_PATH)
            logger.info("Feature names loaded successfully")
        else:
            logger.error(f"Feature names file not found: {FEATURE_NAMES_PATH}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'label_encoder_loaded': label_encoder is not None,
        'feature_names_loaded': feature_names is not None
    })

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
    if model is None or label_encoder is None or feature_names is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.get_json()
        
        if not data or 'symptoms' not in data:
            return jsonify({'error': 'No symptoms provided'}), 400
        
        symptoms = data['symptoms']
        
        # Validate symptoms
        if not isinstance(symptoms, dict):
            return jsonify({'error': 'Symptoms must be a dictionary'}), 400
        
        # Create feature vector
        feature_vector = []
        for feature in feature_names:
            value = symptoms.get(feature, 0)
            if not isinstance(value, (int, float)):
                return jsonify({'error': f'Invalid value for symptom {feature}'}), 400
            feature_vector.append(float(value))
        
        # Make prediction
        features = np.array([feature_vector])
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        # Get diagnosis name
        diagnosis = label_encoder.inverse_transform([prediction])[0]
        
        # Get top 3 predictions with probabilities
        top_3_indices = np.argsort(probabilities)[-3:][::-1]
        top_3_diagnoses = label_encoder.inverse_transform(top_3_indices)
        top_3_probabilities = probabilities[top_3_indices]
        
        # Create response
        response = {
            'diagnosis': diagnosis,
            'confidence': float(probabilities[prediction]),
            'top_3_predictions': [
                {
                    'diagnosis': diag,
                    'confidence': float(prob)
                }
                for diag, prob in zip(top_3_diagnoses, top_3_probabilities)
            ],
            'input_symptoms': symptoms
        }
        
        logger.info(f"Prediction made: {diagnosis} (confidence: {probabilities[prediction]:.2%})")
        
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
        app.run(host='0.0.0.0', port=5001, debug=True)
    else:
        logger.error("Failed to load model. Please train the model first.")
        exit(1)
