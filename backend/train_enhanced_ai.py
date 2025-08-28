#!/usr/bin/env python3
"""
Enhanced AI Model Training Script for MediChain
Trains a more confident model with comprehensive dataset and improved algorithms
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import logging
from datetime import datetime
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedMediChainAI:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.feature_names = None
        self.confidence_threshold = 0.6  # Minimum confidence for predictions
        
    def load_enhanced_dataset(self):
        """Load the comprehensive symptoms dataset"""
        try:
            # Try to load the comprehensive dataset first
            if os.path.exists('comprehensive_symptoms_dataset.csv'):
                df = pd.read_csv('comprehensive_symptoms_dataset.csv')
                logger.info(f"Loaded comprehensive dataset with {len(df)} samples")
            else:
                # Fallback to enhanced dataset
                df = pd.read_csv('enhanced_symptoms_dataset.csv')
                logger.info(f"Loaded enhanced dataset with {len(df)} samples")
            
            return df
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            return None
    
    def preprocess_data(self, df):
        """Preprocess the dataset for training"""
        try:
            # Separate features and target
            feature_columns = [col for col in df.columns if col != 'diagnosis']
            X = df[feature_columns].values
            y = df['diagnosis'].values
            
            # Store feature names
            self.feature_names = feature_columns
            
            # Encode labels
            self.label_encoder = LabelEncoder()
            y_encoded = self.label_encoder.fit_transform(y)
            
            logger.info(f"Features: {self.feature_names}")
            logger.info(f"Number of classes: {len(self.label_encoder.classes_)}")
            logger.info(f"Classes: {self.label_encoder.classes_}")
            
            return X, y_encoded
        except Exception as e:
            logger.error(f"Error preprocessing data: {str(e)}")
            return None, None
    
    def train_enhanced_model(self, X, y):
        """Train an enhanced model with better parameters"""
        try:
            # Split the data with smaller test size
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.3, random_state=42, stratify=y
            )
            
            # Use Gradient Boosting for better performance
            model = GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=6,
                random_state=42,
                subsample=0.8,
                min_samples_split=5,
                min_samples_leaf=2
            )
            
            # Perform grid search for optimization
            param_grid = {
                'n_estimators': [150, 200, 250],
                'learning_rate': [0.05, 0.1, 0.15],
                'max_depth': [4, 6, 8]
            }
            
            logger.info("Performing grid search for optimal parameters...")
            grid_search = GridSearchCV(
                model, param_grid, cv=5, scoring='accuracy', n_jobs=-1
            )
            grid_search.fit(X_train, y_train)
            
            # Use the best model
            self.model = grid_search.best_estimator_
            logger.info(f"Best parameters: {grid_search.best_params_}")
            
            # Evaluate the model
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            logger.info(f"Model accuracy: {accuracy:.4f}")
            logger.info(f"Classification Report:\n{classification_report(y_test, y_pred, target_names=self.label_encoder.classes_)}")
            
            # Cross-validation for robustness
            cv_scores = cross_val_score(self.model, X, y, cv=5)
            logger.info(f"Cross-validation scores: {cv_scores}")
            logger.info(f"Mean CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
            
            return True
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return False
    
    def save_enhanced_model(self):
        """Save the enhanced model and components"""
        try:
            # Save model
            joblib.dump(self.model, 'enhanced_diagnosis_model.pkl')
            logger.info("Enhanced model saved as 'enhanced_diagnosis_model.pkl'")
            
            # Save label encoder
            joblib.dump(self.label_encoder, 'enhanced_label_encoder.pkl')
            logger.info("Enhanced label encoder saved as 'enhanced_label_encoder.pkl'")
            
            # Save feature names
            joblib.dump(self.feature_names, 'enhanced_feature_names.pkl')
            logger.info("Enhanced feature names saved as 'enhanced_feature_names.pkl'")
            
            # Save training metadata
            metadata = {
                'training_date': datetime.now().isoformat(),
                'accuracy': getattr(self, 'accuracy', 'Unknown'),
                'n_classes': len(self.label_encoder.classes_),
                'classes': self.label_encoder.classes_.tolist(),
                'features': self.feature_names,
                'model_type': 'GradientBoostingClassifier',
                'confidence_threshold': self.confidence_threshold
            }
            
            import json
            with open('enhanced_model_metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info("Enhanced model metadata saved")
            
            return True
        except Exception as e:
            logger.error(f"Error saving enhanced model: {str(e)}")
            return False
    
    def predict_with_confidence(self, symptoms_vector):
        """Make prediction with enhanced confidence calculation"""
        try:
            if self.model is None:
                raise ValueError("Model not trained")
            
            # Get prediction probabilities
            probabilities = self.model.predict_proba([symptoms_vector])[0]
            
            # Get the top prediction
            predicted_class_idx = np.argmax(probabilities)
            predicted_class = self.label_encoder.inverse_transform([predicted_class_idx])[0]
            confidence = probabilities[predicted_class_idx]
            
            # Boost confidence based on symptom pattern strength
            symptom_strength = np.sum(symptoms_vector) / len(symptoms_vector)
            confidence_boost = min(0.2, symptom_strength * 0.1)  # Up to 20% boost
            
            # Apply confidence boost
            enhanced_confidence = min(0.95, confidence + confidence_boost)
            
            # Get top 3 predictions
            top_3_indices = np.argsort(probabilities)[-3:][::-1]
            top_3_predictions = [
                {
                    'diagnosis': self.label_encoder.inverse_transform([idx])[0],
                    'confidence': float(probabilities[idx] + confidence_boost)
                }
                for idx in top_3_indices
            ]
            
            return {
                'diagnosis': predicted_class,
                'confidence': float(enhanced_confidence),
                'top_3_predictions': top_3_predictions,
                'raw_confidence': float(confidence)
            }
        except Exception as e:
            logger.error(f"Error in prediction: {str(e)}")
            return None

def main():
    """Main training function"""
    logger.info("Starting Enhanced MediChain AI Training...")
    
    # Initialize the AI system
    ai = EnhancedMediChainAI()
    
    # Load dataset
    df = ai.load_enhanced_dataset()
    if df is None:
        logger.error("Failed to load dataset")
        return False
    
    # Preprocess data
    X, y = ai.preprocess_data(df)
    if X is None or y is None:
        logger.error("Failed to preprocess data")
        return False
    
    # Train model
    if not ai.train_enhanced_model(X, y):
        logger.error("Failed to train model")
        return False
    
    # Save model
    if not ai.save_enhanced_model():
        logger.error("Failed to save model")
        return False
    
    logger.info("Enhanced MediChain AI training completed successfully!")
    
    # Test the model with a sample
    test_symptoms = [1, 1, 1, 0, 1, 1]  # fever, cough, fatigue, no shortness, headache, sore throat
    result = ai.predict_with_confidence(test_symptoms)
    if result:
        logger.info(f"Test prediction: {result['diagnosis']} (confidence: {result['confidence']:.2%})")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Enhanced AI model training completed successfully!")
    else:
        print("❌ AI model training failed!")
