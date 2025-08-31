#!/usr/bin/env python3
"""
Test script to verify the enhanced model contains all expected diagnoses
"""
import pickle
import pandas as pd

def test_enhanced_model():
    try:
        # Load enhanced label encoder
        with open('enhanced_label_encoder.pkl', 'rb') as f:
            label_encoder = pickle.load(f)
        
        print(f"Enhanced Label Encoder Classes: {len(label_encoder.classes_)}")
        print("Diagnoses in enhanced model:")
        for i, diagnosis in enumerate(sorted(label_encoder.classes_)):
            print(f"{i+1:2d}. {diagnosis}")
        
        # Check specific diagnoses that were causing errors
        test_diagnoses = ['Flu', 'Conjunctivitis', 'Tension Headache']
        print(f"\nChecking for specific diagnoses:")
        for diagnosis in test_diagnoses:
            if diagnosis in label_encoder.classes_:
                print(f"✅ {diagnosis} - FOUND")
            else:
                print(f"❌ {diagnosis} - NOT FOUND")
        
        # Load dataset to verify
        df = pd.read_csv('enhanced_comprehensive_symptoms_dataset.csv')
        unique_diagnoses = df.iloc[:, -1].unique()
        print(f"\nDataset contains {len(unique_diagnoses)} unique diagnoses:")
        for diagnosis in sorted(unique_diagnoses):
            print(f"  - {diagnosis}")
            
        return True
    except Exception as e:
        print(f"Error testing enhanced model: {e}")
        return False

if __name__ == "__main__":
    test_enhanced_model()
