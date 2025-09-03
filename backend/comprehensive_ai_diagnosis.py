#!/usr/bin/env python3
"""
Updated AI Diagnosis Service with Duration and Intensity Support
Supports comprehensive natural language processing and enhanced features
"""

import pickle
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import re
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveAIDiagnosis:
    """Enhanced AI diagnosis system with duration and intensity support"""
    
    def __init__(self, model_path='final_comprehensive_model.pkl', 
                 encoder_path='final_comprehensive_encoder.pkl',
                 features_path='final_comprehensive_features.pkl'):
        """Initialize the comprehensive AI diagnosis system"""
        
        try:
            # Load model components
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            with open(features_path, 'rb') as f:
                self.feature_names = pickle.load(f)
            
            logger.info(f"Model loaded successfully")
            logger.info(f"Features: {len(self.feature_names)}")
            logger.info(f"Supported diagnoses: {len(self.label_encoder.classes_)}")
            
            # Initialize symptom parser
            self.symptom_parser = EnhancedSymptomParser()
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def diagnose(self, symptoms_text: str, duration_text: str = "", 
                intensity_text: str = "") -> Dict:
        """
        Comprehensive diagnosis with natural language processing
        
        Args:
            symptoms_text: Natural language description of symptoms
            duration_text: Duration information (optional)
            intensity_text: Intensity information (optional)
        
        Returns:
            Dictionary with diagnosis results and confidence
        """
        try:
            # Parse symptoms and extract features
            parsed_result = self.symptom_parser.parse_comprehensive(
                symptoms_text, duration_text, intensity_text
            )
            
            # Create feature vector
            feature_vector = self._create_feature_vector(parsed_result)
            
            # Make prediction
            prediction = self.model.predict([feature_vector])[0]
            probabilities = self.model.predict_proba([feature_vector])[0]
            
            # Get diagnosis name
            diagnosis = self.label_encoder.inverse_transform([prediction])[0]
            confidence = float(probabilities[prediction])
            
            # Get top 3 predictions
            top_indices = np.argsort(probabilities)[-3:][::-1]
            top_predictions = [
                {
                    'diagnosis': self.label_encoder.inverse_transform([idx])[0],
                    'confidence': float(probabilities[idx])
                }
                for idx in top_indices
            ]
            
            result = {
                'primary_diagnosis': diagnosis,
                'confidence': confidence,
                'top_predictions': top_predictions,
                'parsed_symptoms': parsed_result['symptoms'],
                'duration_days': parsed_result['duration_days'],
                'intensity': parsed_result['intensity'],
                'feature_vector': dict(zip(self.feature_names, feature_vector)),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Diagnosis: {diagnosis} (confidence: {confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Error in diagnosis: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _create_feature_vector(self, parsed_result: Dict) -> List[float]:
        """Create feature vector from parsed symptoms"""
        
        # Define expected symptom features (matching model training)
        expected_symptoms = [
            'fever', 'cough', 'fatigue', 'shortness_of_breath', 'headache', 
            'sore_throat', 'nausea', 'dizziness', 'body_aches', 'runny_nose', 
            'chest_pain', 'diarrhea', 'loss_of_taste', 'loss_of_smell'
        ]
        
        # Create symptom vector
        symptom_vector = []
        for symptom in expected_symptoms:
            if symptom in parsed_result['symptoms']:
                symptom_vector.append(1.0)
            else:
                symptom_vector.append(0.0)
        
        # Add duration (numeric)
        duration_days = float(parsed_result.get('duration_days', 7))  # Default 7 days
        symptom_vector.append(duration_days)
        
        # Add intensity (numeric)
        intensity_mapping = {
            'mild': 1.0,
            'moderate': 2.0,
            'severe': 3.0,
            'unspecified': 0.0
        }
        intensity_numeric = intensity_mapping.get(
            parsed_result.get('intensity', 'moderate'), 2.0
        )
        symptom_vector.append(intensity_numeric)
        
        return symptom_vector

class EnhancedSymptomParser:
    """Enhanced symptom parser with duration and intensity extraction"""
    
    def __init__(self):
        # Comprehensive symptom keywords
        self.symptom_keywords = {
            'fever': [
                'fever', 'temperature', 'hot', 'burning up', 'feverish', 
                'high temp', 'pyrexia', 'febrile', 'warm', 'overheated'
            ],
            'cough': [
                'cough', 'coughing', 'hack', 'dry cough', 'wet cough', 
                'productive cough', 'persistent cough', 'hacking', 'barking cough'
            ],
            'fatigue': [
                'tired', 'fatigue', 'exhausted', 'weakness', 'weary', 
                'drained', 'lethargic', 'sleepy', 'worn out', 'depleted'
            ],
            'shortness_of_breath': [
                'shortness of breath', 'breathless', 'difficulty breathing', 
                'hard to breathe', 'winded', 'dyspnea', 'suffocating', 'gasping'
            ],
            'headache': [
                'headache', 'head pain', 'migraine', 'head hurts', 
                'skull pain', 'cranial pain', 'temple pain', 'forehead pain'
            ],
            'sore_throat': [
                'sore throat', 'throat pain', 'scratchy throat', 'throat hurts', 
                'pharyngitis', 'swollen throat', 'raw throat', 'burning throat'
            ],
            'nausea': [
                'nausea', 'nauseous', 'queasy', 'sick to stomach', 
                'feeling sick', 'want to vomit', 'motion sickness', 'car sick'
            ],
            'dizziness': [
                'dizzy', 'dizziness', 'lightheaded', 'vertigo', 'spinning', 
                'unsteady', 'balance problems', 'wobbly', 'off balance'
            ],
            'body_aches': [
                'body aches', 'muscle aches', 'joint pain', 'aching', 
                'soreness', 'stiffness', 'muscle pain', 'joint aches', 'myalgia'
            ],
            'runny_nose': [
                'runny nose', 'nasal discharge', 'stuffy nose', 'congestion', 
                'blocked nose', 'rhinorrhea', 'sniffles', 'post nasal drip'
            ],
            'chest_pain': [
                'chest pain', 'chest discomfort', 'chest tightness', 
                'heart pain', 'sternum pain', 'ribcage pain', 'breathing pain'
            ],
            'diarrhea': [
                'diarrhea', 'loose stools', 'watery stools', 'frequent bowel', 
                'runny stools', 'liquid stool', 'bowel problems', 'stomach runs'
            ],
            'loss_of_taste': [
                'loss of taste', 'can\'t taste', 'no taste', 'taste gone', 
                'ageusia', 'taste buds not working', 'food tastes bland'
            ],
            'loss_of_smell': [
                'loss of smell', 'can\'t smell', 'no smell', 'smell gone', 
                'anosmia', 'nose doesn\'t work', 'can\'t detect odors'
            ]
        }
        
        # Duration patterns (more comprehensive)
        self.duration_patterns = [
            (r'(\d+)\s*(day|days)', lambda m: int(m.group(1))),
            (r'(\d+)\s*(week|weeks)', lambda m: int(m.group(1)) * 7),
            (r'(\d+)\s*(month|months)', lambda m: int(m.group(1)) * 30),
            (r'since\s+(\d+)\s*(day|days)\s+ago', lambda m: int(m.group(1))),
            (r'for\s+(\d+)\s*(day|days)', lambda m: int(m.group(1))),
            (r'about\s+(\d+)\s*(day|days)', lambda m: int(m.group(1))),
            (r'around\s+(\d+)\s*(day|days)', lambda m: int(m.group(1))),
            (r'yesterday', lambda m: 1),
            (r'today', lambda m: 1),
            (r'few days', lambda m: 3),
            (r'several days', lambda m: 5),
            (r'last week', lambda m: 7),
            (r'past week', lambda m: 7),
            (r'this week', lambda m: 3),
            (r'two weeks', lambda m: 14),
            (r'couple weeks', lambda m: 14),
            (r'last month', lambda m: 30),
            (r'past month', lambda m: 30),
            (r'chronic', lambda m: 90),
            (r'ongoing', lambda m: 30),
            (r'persistent', lambda m: 14),
            (r'recent', lambda m: 3),
            (r'acute', lambda m: 3),
            (r'sudden', lambda m: 1),
            (r'gradual', lambda m: 7)
        ]
        
        # Intensity patterns
        self.intensity_patterns = {
            'mild': [
                'mild', 'slight', 'minor', 'light', 'gentle', 'low', 
                'barely', 'little bit', 'somewhat', 'not too bad'
            ],
            'moderate': [
                'moderate', 'medium', 'average', 'normal', 'typical', 
                'noticeable', 'considerable', 'fair', 'decent'
            ],
            'severe': [
                'severe', 'intense', 'extreme', 'terrible', 'awful', 
                'excruciating', 'unbearable', 'very', 'really bad', 'horrible'
            ]
        }
    
    def parse_comprehensive(self, symptoms_text: str, duration_text: str = "", 
                          intensity_text: str = "") -> Dict:
        """Parse comprehensive symptom information"""
        
        # Combine all text for parsing
        full_text = f"{symptoms_text} {duration_text} {intensity_text}".lower()
        
        # Extract symptoms
        detected_symptoms = self._extract_symptoms(full_text)
        
        # Extract duration
        duration_days = self._extract_duration(full_text)
        
        # Extract intensity
        intensity = self._extract_intensity(full_text)
        
        return {
            'symptoms': detected_symptoms,
            'duration_days': duration_days,
            'intensity': intensity,
            'raw_text': symptoms_text
        }
    
    def _extract_symptoms(self, text: str) -> List[str]:
        """Extract symptoms from text"""
        detected = []
        
        for symptom, keywords in self.symptom_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    detected.append(symptom)
                    break
        
        return detected
    
    def _extract_duration(self, text: str) -> int:
        """Extract duration in days from text"""
        
        for pattern, converter in self.duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return converter(match)
                except:
                    continue
        
        # Default to 7 days if no duration found
        return 7
    
    def _extract_intensity(self, text: str) -> str:
        """Extract intensity from text"""
        
        for intensity, keywords in self.intensity_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    return intensity
        
        # Default to moderate
        return 'moderate'
    
    def _was_duration_detected(self, text: str) -> bool:
        """Check if duration was actually detected from text (not defaulted)"""
        text = text.lower()
        for pattern, _ in self.duration_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _was_intensity_detected(self, text: str) -> bool:
        """Check if intensity was actually detected from text (not defaulted)"""
        text = text.lower()
        for intensity, keywords in self.intensity_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    return True
        return False

# Example usage and testing
def test_comprehensive_diagnosis():
    """Test the comprehensive diagnosis system"""
    
    print("🧪 Testing Comprehensive AI Diagnosis System")
    print("="*60)
    
    try:
        # Initialize diagnosis system
        ai_diagnosis = ComprehensiveAIDiagnosis()
        
        # Test cases
        test_cases = [
            {
                'symptoms': "I have a severe headache and fever for 3 days, feeling very tired",
                'duration': "3 days",
                'intensity': "severe"
            },
            {
                'symptoms': "mild cough and runny nose since yesterday, sore throat",
                'duration': "1 day", 
                'intensity': "mild"
            },
            {
                'symptoms': "chest pain, shortness of breath, very intense for about a week",
                'duration': "1 week",
                'intensity': "severe"
            }
        ]
        
        for i, case in enumerate(test_cases):
            print(f"\n--- Test Case {i+1} ---")
            print(f"Input: {case['symptoms']}")
            
            result = ai_diagnosis.diagnose(
                case['symptoms'], 
                case['duration'], 
                case['intensity']
            )
            
            if 'error' not in result:
                print(f"Diagnosis: {result['primary_diagnosis']}")
                print(f"Confidence: {result['confidence']:.3f}")
                print(f"Duration: {result['duration_days']} days")
                print(f"Intensity: {result['intensity']}")
                print(f"Symptoms: {result['parsed_symptoms']}")
            else:
                print(f"Error: {result['error']}")
        
        print("\n✅ Testing completed successfully!")
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")

if __name__ == "__main__":
    test_comprehensive_diagnosis()
