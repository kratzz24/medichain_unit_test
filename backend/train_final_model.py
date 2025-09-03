#!/usr/bin/env python3
"""
Fixed Comprehensive Model Training with Correct Column Names
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

def train_final_model():
    print("="*80)
    print("TRAINING FINAL COMPREHENSIVE MODEL")
    print("="*80)
    
    # Load dataset
    print("📊 Loading comprehensive enhanced dataset...")
    df = pd.read_csv('comprehensive_enhanced_dataset.csv')
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Unique diagnoses: {df['diagnosis'].nunique()}")
    
    # Get the actual symptom columns from the dataset
    symptom_features = [
        'fever', 'cough', 'fatigue', 'shortness_of_breath', 'headache', 
        'sore_throat', 'nausea', 'dizziness', 'body_aches', 'runny_nose', 
        'chest_pain', 'diarrhea', 'loss_of_taste', 'loss_of_smell'
    ]
    
    print(f"Symptom features: {symptom_features}")
    
    # Handle missing values
    print("\n🔧 Preprocessing data...")
    for col in symptom_features:
        df[col].fillna(0, inplace=True)
    
    # Handle duration and intensity
    df['duration_days'].fillna(df['duration_days'].median(), inplace=True)
    
    # Create intensity mapping
    intensity_mapping = {
        'mild': 1,
        'moderate': 2, 
        'severe': 3,
        'unspecified': 0
    }
    
    df['intensity_numeric'] = df['intensity'].map(intensity_mapping)
    df['intensity_numeric'].fillna(0, inplace=True)
    
    # Prepare features
    all_features = symptom_features + ['duration_days', 'intensity_numeric']
    X = df[all_features]
    y = df['diagnosis']
    
    print(f"Features shape: {X.shape}")
    print(f"Number of features: {len(all_features)}")
    print(f"Target shape: {y.shape}")
    print(f"Unique diagnoses: {y.nunique()}")
    
    # Check for missing values
    print(f"\nMissing values check:")
    print(X.isnull().sum().sum())
    
    # Encode labels
    print("\n🏷️ Encoding labels...")
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Split data
    print("🔄 Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    
    # Train model
    print("\n🚀 Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=3,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate model
    print("📈 Evaluating model...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✅ Model Performance:")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Number of classes: {len(label_encoder.classes_)}")
    
    # Feature importance
    print("\n🔍 Feature Importance:")
    importance = model.feature_importances_
    feature_importance_df = pd.DataFrame({
        'feature': all_features,
        'importance': importance
    }).sort_values('importance', ascending=False)
    
    print("Top 10 most important features:")
    for i, row in feature_importance_df.head(10).iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    # Save model and components
    print("\n💾 Saving model...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save with timestamp
    model_files = {
        'model': f'final_model_{timestamp}.pkl',
        'encoder': f'final_encoder_{timestamp}.pkl',
        'features': f'final_features_{timestamp}.pkl'
    }
    
    # Also save as current versions
    current_files = {
        'model': 'final_comprehensive_model.pkl',
        'encoder': 'final_comprehensive_encoder.pkl',
        'features': 'final_comprehensive_features.pkl'
    }
    
    # Save all files
    for key in ['model', 'encoder', 'features']:
        obj = model if key == 'model' else (label_encoder if key == 'encoder' else all_features)
        
        # Save timestamped version
        with open(model_files[key], 'wb') as f:
            pickle.dump(obj, f)
        
        # Save current version
        with open(current_files[key], 'wb') as f:
            pickle.dump(obj, f)
    
    print(f"Model saved as:")
    for key, path in current_files.items():
        print(f"  - {path}")
    
    # Test the saved model
    print("\n🧪 Testing saved model...")
    with open('final_comprehensive_model.pkl', 'rb') as f:
        loaded_model = pickle.load(f)
    with open('final_comprehensive_encoder.pkl', 'rb') as f:
        loaded_encoder = pickle.load(f)
    with open('final_comprehensive_features.pkl', 'rb') as f:
        loaded_features = pickle.load(f)
    
    # Test prediction
    test_sample = X_test.iloc[0:1]
    prediction = loaded_model.predict(test_sample)
    diagnosis = loaded_encoder.inverse_transform(prediction)
    
    print(f"Test prediction successful: {diagnosis[0]}")
    
    print("\n🎉 Training Complete!")
    print(f"Final model accuracy: {accuracy:.4f}")
    print(f"Supports {len(label_encoder.classes_)} diagnoses")
    print(f"Uses {len(all_features)} features including duration and intensity")
    
    return accuracy, len(label_encoder.classes_), all_features

if __name__ == "__main__":
    train_final_model()
