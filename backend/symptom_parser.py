"""
Symptom Parser for MediChain AI

This module provides functionality to extract symptoms from natural language text
and convert them to the feature vector format required by the trained diagnosis model.
"""

import os
import re
import joblib
import logging
from typing import Dict, List, Set, Tuple, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SymptomParser:
    """
    A class to parse natural language symptom descriptions and convert them
    to the feature vector format required by the trained diagnosis model.
    """
    
    def __init__(self, model_path: str = "."):
        """
        Initialize the SymptomParser with the set of features from the model.
        
        Args:
            model_path (str): Path to the directory containing model files
        """
        self.model_path = model_path
        self.feature_names = []
        self.load_feature_names()
        
        # Comprehensive symptom keyword database - maps model features to common expressions
        self.symptom_keywords = {
            'fever': [
                'fever', 'high temperature', 'hot', 'burning up', 'temperature', 
                'chills', 'feverish', 'high temp', 'hot flashes', 'pyrexia', 'febrile'
            ],
            'cough': [
                'cough', 'coughing', 'hack', 'wheeze', 'phlegm', 'mucus', 
                'chest congestion', 'productive cough', 'dry cough', 'barking cough',
                'persistent cough', 'hacking'
            ],
            'fatigue': [
                'tired', 'fatigue', 'exhausted', 'weak', 'weary', 'drained', 
                'lethargic', 'sleepy', 'worn out', 'no energy', 'exhaustion', 
                'lack of energy', 'tired all the time'
            ],
            'shortness_of_breath': [
                'breathless', 'short of breath', 'breathing difficulty', 'wheezing', 
                'gasping', 'can\'t breathe', 'trouble breathing', 'dyspnea', 'winded',
                'hard to breathe', 'difficulty breathing', 'labored breathing', 
                'heavy breathing', 'panting', 'shortness of breath', 'breath'
            ],
            'headache': [
                'headache', 'head pain', 'migraine', 'head pressure', 'skull pain', 
                'temple pain', 'cephalgia', 'head ache', 'throbbing head', 'tension headache',
                'sinus headache', 'head throbbing', 'pounding head', 'head is pounding', 'pounding'
            ],
            'sore_throat': [
                'sore throat', 'throat pain', 'scratchy throat', 'swollen throat', 
                'throat irritation', 'pharyngitis', 'throat ache', 'painful swallowing',
                'throat discomfort', 'burning throat', 'irritated throat'
            ]
        }
        
        # Common modifier words and their intensity values
        self.modifiers = {
            'mild': 0.5,
            'slight': 0.3,
            'little': 0.2,
            'moderate': 0.7,
            'bad': 0.8,
            'severe': 1.0,
            'intense': 1.0,
            'extreme': 1.0,
            'very': 0.9,
            'really': 0.9,
            'extremely': 1.0,
            'slightly': 0.3
        }
        
    def load_feature_names(self):
        """Load feature names from the saved model file"""
        try:
            feature_path = os.path.join(self.model_path, "enhanced_feature_names.pkl")
            if not os.path.exists(feature_path):
                feature_path = os.path.join(self.model_path, "feature_names.pkl")
            
            if os.path.exists(feature_path):
                self.feature_names = joblib.load(feature_path)
                logger.info(f"Loaded {len(self.feature_names)} features: {self.feature_names}")
            else:
                logger.error(f"Feature names file not found at {feature_path}")
        except Exception as e:
            logger.error(f"Error loading feature names: {str(e)}")
    
    def parse_symptoms(self, symptom_text: str) -> Dict[str, float]:
        """
        Parse symptoms from natural language text and map to model features.
        
        Args:
            symptom_text (str): Natural language description of symptoms
            
        Returns:
            Dict[str, float]: Dictionary with feature names as keys and values (0-1)
        """
        if not symptom_text:
            logger.warning("Empty symptom text provided")
            return {feature: 0.0 for feature in self.feature_names}
        
        # Preprocess text
        text = symptom_text.lower().strip()
        logger.info(f"Processing symptom text: '{text}'")
        
        # Initialize result dictionary with all features set to 0
        result = {feature: 0.0 for feature in self.feature_names}
        
        # For each known feature, check if any of its keywords are in the text
        for feature in self.feature_names:
            if feature in self.symptom_keywords:
                keywords = self.symptom_keywords[feature]
                
                # Look for exact matches first
                for keyword in keywords:
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    if re.search(pattern, text):
                        # Check for modifiers before the keyword
                        for modifier, value in self.modifiers.items():
                            mod_pattern = r'\b' + re.escape(modifier) + r'\s+' + re.escape(keyword) + r'\b'
                            if re.search(mod_pattern, text):
                                result[feature] = value
                                logger.info(f"Found symptom '{feature}' with modifier '{modifier}' (value: {value})")
                                break
                        else:
                            # No modifier found, use default value of 1.0
                            result[feature] = 1.0
                            logger.info(f"Found symptom '{feature}' (default value: 1.0)")
                        break
            else:
                logger.warning(f"Feature '{feature}' not found in symptom_keywords dictionary")
        
        logger.info(f"Parsed symptoms: {result}")
        return result
    
    def get_feature_vector(self, symptom_text: str) -> List[float]:
        """
        Convert symptom text to a feature vector in the correct order for the model.
        
        Args:
            symptom_text (str): Natural language description of symptoms
            
        Returns:
            List[float]: Feature vector ordered according to model's feature_names
        """
        symptoms_dict = self.parse_symptoms(symptom_text)
        
        # Ensure we're returning features in the exact order expected by the model
        feature_vector = [symptoms_dict.get(feature, 0.0) for feature in self.feature_names]
        logger.info(f"Feature vector: {feature_vector}")
        
        return feature_vector
    
    def extract_symptoms_as_list(self, text: str) -> List[str]:
        """
        Extract a list of symptom names from the text.
        
        Args:
            text (str): Natural language description of symptoms
            
        Returns:
            List[str]: List of symptom names detected in the text
        """
        symptoms_dict = self.parse_symptoms(text)
        return [feature for feature, value in symptoms_dict.items() if value > 0]


# Example usage
if __name__ == "__main__":
    parser = SymptomParser()
    sample_texts = [
        "I have a fever and cough",
        "Severe headache with sore throat",
        "I'm feeling tired and short of breath",
        "High fever, persistent cough, and extreme fatigue"
    ]
    
    for text in sample_texts:
        print(f"\nAnalyzing: '{text}'")
        symptoms = parser.parse_symptoms(text)
        print(f"Detected symptoms: {symptoms}")
        print(f"Feature vector: {parser.get_feature_vector(text)}")
        print(f"Symptom list: {parser.extract_symptoms_as_list(text)}")
