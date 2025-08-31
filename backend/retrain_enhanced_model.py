#!/usr/bin/env python3
"""
Retrain Enhanced AI Model with All 56 Diagnoses
This script will retrain the model to ensure it includes all diagnoses including Conjunctivitis
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retrain_enhanced_model():
    """Retrain the enhanced model with all diagnoses"""
    try:
        # Load the enhanced dataset
        logger.info("Loading enhanced comprehensive symptoms dataset...")
        df = pd.read_csv('enhanced_comprehensive_symptoms_dataset.csv')
        
        # Check dataset structure
        logger.info(f"Dataset shape: {df.shape}")
        logger.info(f"Columns: {list(df.columns)}")
        
        # Prepare features and target
        X = df.iloc[:, :-1]  # All columns except last (diagnosis)
        y = df.iloc[:, -1]   # Last column (diagnosis)
        
        logger.info(f"Features shape: {X.shape}")
        logger.info(f"Target shape: {y.shape}")
        logger.info(f"Unique diagnoses: {len(y.unique())}")
        
        # Print all unique diagnoses
        unique_diagnoses = sorted(y.unique())
        logger.info("All diagnoses in dataset:")
        for i, diagnosis in enumerate(unique_diagnoses):
            logger.info(f"  {i+1:2d}. {diagnosis}")
        
        # Check for specific problematic diagnoses
        problem_diagnoses = ['Flu', 'Conjunctivitis', 'Tension Headache']
        for diagnosis in problem_diagnoses:
            if diagnosis in unique_diagnoses:
                count = (y == diagnosis).sum()
                logger.info(f"✅ {diagnosis}: {count} samples")
            else:
                logger.error(f"❌ {diagnosis}: NOT FOUND in dataset")
        
        # Encode labels
        logger.info("Encoding labels...")
        label_encoder = LabelEncoder()
        y_encoded = label_encoder.fit_transform(y)
        
        logger.info(f"Label encoder classes: {len(label_encoder.classes_)}")
        
        # Split data
        logger.info("Splitting data...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Train model
        logger.info("Training Random Forest model...")
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate model
        logger.info("Evaluating model...")
        train_accuracy = model.score(X_train, y_train)
        test_accuracy = model.score(X_test, y_test)
        
        logger.info(f"Training accuracy: {train_accuracy:.4f}")
        logger.info(f"Testing accuracy: {test_accuracy:.4f}")
        
        # Create prescriptions map for all diagnoses
        logger.info("Creating prescriptions map...")
        prescriptions_map = {}
        
        # Basic prescriptions for common conditions
        basic_prescriptions = {
            'Flu': 'Rest, fluids, antipyretics (acetaminophen/ibuprofen), antiviral if severe',
            'Common Cold': 'Rest, fluids, decongestants, throat lozenges',
            'Conjunctivitis': 'Antibiotic eye drops if bacterial, antihistamines if allergic',
            'Tension Headache': 'Rest, hydration, acetaminophen or ibuprofen, stress management',
            'Migraine': 'Rest in dark room, triptans, avoid triggers',
            'COVID-19': 'Isolation, rest, fluids, monitor oxygen levels, seek medical care if severe',
            'Pneumonia': 'Antibiotics if bacterial, rest, fluids, oxygen therapy if needed',
            'Bronchitis': 'Rest, fluids, cough suppressants, bronchodilators if needed',
            'Asthma': 'Bronchodilators, inhaled corticosteroids, avoid triggers',
            'Allergies': 'Antihistamines, avoid allergens, nasal corticosteroids',
            'Sinusitis': 'Decongestants, nasal irrigation, antibiotics if bacterial',
            'Strep Throat': 'Antibiotics (penicillin), pain relievers, throat lozenges',
            'Food Poisoning': 'Fluids, electrolyte replacement, rest, bland diet',
            'Gastroenteritis': 'Fluids, electrolyte replacement, probiotics, bland diet',
            'UTI': 'Antibiotics, increased fluid intake, cranberry juice',
            'Hypertension': 'Lifestyle changes, ACE inhibitors or other antihypertensives',
            'Diabetes': 'Blood sugar monitoring, insulin/medications, diet management',
            'Arthritis': 'NSAIDs, physical therapy, joint protection',
            'Depression': 'Antidepressants, therapy, lifestyle changes',
            'Anxiety': 'Anxiolytics, therapy, stress management techniques'
        }
        
        # Create prescriptions for all diagnoses
        for diagnosis in unique_diagnoses:
            if diagnosis in basic_prescriptions:
                prescriptions_map[diagnosis] = basic_prescriptions[diagnosis]
            else:
                prescriptions_map[diagnosis] = f'Consult healthcare provider for {diagnosis} treatment'
        
        # Save all components
        logger.info("Saving enhanced model components...")
        
        # Save model
        with open('enhanced_diagnosis_model.pkl', 'wb') as f:
            pickle.dump(model, f)
        logger.info("✅ Enhanced model saved")
        
        # Save label encoder
        with open('enhanced_label_encoder.pkl', 'wb') as f:
            pickle.dump(label_encoder, f)
        logger.info("✅ Enhanced label encoder saved")
        
        # Save feature names
        feature_names = list(X.columns)
        with open('enhanced_feature_names.pkl', 'wb') as f:
            pickle.dump(feature_names, f)
        logger.info("✅ Enhanced feature names saved")
        
        # Save prescriptions map
        with open('enhanced_prescriptions_map.pkl', 'wb') as f:
            pickle.dump(prescriptions_map, f)
        logger.info("✅ Enhanced prescriptions map saved")
        
        # Verify saved files by loading them
        logger.info("Verifying saved files...")
        
        # Test loading model
        with open('enhanced_diagnosis_model.pkl', 'rb') as f:
            loaded_model = pickle.load(f)
        
        # Test loading label encoder
        with open('enhanced_label_encoder.pkl', 'rb') as f:
            loaded_le = pickle.load(f)
        
        logger.info(f"Verified: Model loaded with {len(loaded_le.classes_)} classes")
        
        # Test predictions on problematic diagnoses
        logger.info("Testing predictions for problematic diagnoses...")
        
        # Test with sample data for each problematic diagnosis
        test_samples = {
            'Conjunctivitis': [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],  # fatigue, headache
            'Flu': [1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0],  # fever, cough, fatigue, headache, sore_throat, body_aches
            'Tension Headache': [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # fatigue, headache
        }
        
        for diagnosis, sample in test_samples.items():
            try:
                prediction = loaded_model.predict([sample])
                predicted_diagnosis = loaded_le.inverse_transform(prediction)[0]
                logger.info(f"Test prediction for {diagnosis}: {predicted_diagnosis}")
            except Exception as e:
                logger.error(f"Error predicting {diagnosis}: {e}")
        
        logger.info("✅ Enhanced model retraining completed successfully!")
        logger.info(f"Model supports {len(loaded_le.classes_)} diagnoses")
        
        return True
        
    except Exception as e:
        logger.error(f"Error retraining enhanced model: {e}")
        return False

if __name__ == "__main__":
    retrain_enhanced_model()
