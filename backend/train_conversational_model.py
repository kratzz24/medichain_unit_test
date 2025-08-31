import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import warnings
warnings.filterwarnings('ignore')

# Create conversational diagnosis training dataset
def create_conversational_dataset():
    """Create a comprehensive dataset for conversational diagnosis"""
    
    # Define symptoms and their conversational variations
    symptoms = [
        'fever', 'cough', 'fatigue', 'shortness_of_breath', 'headache',
        'sore_throat', 'nausea', 'dizziness', 'body_aches', 'runny_nose',
        'chest_pain', 'diarrhea', 'loss_of_taste', 'loss_of_smell'
    ]
    
    # Define medical conditions with symptom patterns
    conditions_patterns = {
        'Common Cold': {
            'primary': ['runny_nose', 'sore_throat', 'cough'],
            'secondary': ['fatigue', 'headache'],
            'severity': 'mild'
        },
        'Flu': {
            'primary': ['fever', 'body_aches', 'fatigue'],
            'secondary': ['headache', 'cough', 'sore_throat'],
            'severity': 'moderate'
        },
        'COVID-19': {
            'primary': ['fever', 'cough', 'fatigue'],
            'secondary': ['loss_of_taste', 'loss_of_smell', 'shortness_of_breath'],
            'severity': 'moderate-severe'
        },
        'Pneumonia': {
            'primary': ['fever', 'cough', 'shortness_of_breath'],
            'secondary': ['chest_pain', 'fatigue'],
            'severity': 'severe'
        },
        'Bronchitis': {
            'primary': ['cough', 'fatigue'],
            'secondary': ['chest_pain', 'shortness_of_breath'],
            'severity': 'moderate'
        },
        'Sinusitis': {
            'primary': ['headache', 'runny_nose'],
            'secondary': ['fatigue', 'sore_throat'],
            'severity': 'mild-moderate'
        },
        'Migraine': {
            'primary': ['headache'],
            'secondary': ['nausea', 'dizziness'],
            'severity': 'severe'
        },
        'Tension Headache': {
            'primary': ['headache'],
            'secondary': ['fatigue'],
            'severity': 'mild-moderate'
        },
        'Gastroenteritis': {
            'primary': ['nausea', 'diarrhea'],
            'secondary': ['fatigue', 'body_aches'],
            'severity': 'moderate'
        },
        'Allergic Rhinitis': {
            'primary': ['runny_nose'],
            'secondary': ['sore_throat', 'fatigue'],
            'severity': 'mild'
        }
    }
    
    # Generate training samples
    training_data = []
    
    for condition, pattern in conditions_patterns.items():
        # Generate 50 samples per condition for robust training
        for i in range(50):
            sample = {symptom: 0 for symptom in symptoms}
            
            # Always include primary symptoms
            for primary_symptom in pattern['primary']:
                if primary_symptom in symptoms:
                    sample[primary_symptom] = 1
            
            # Randomly include secondary symptoms (70% chance)
            for secondary_symptom in pattern['secondary']:
                if secondary_symptom in symptoms and np.random.random() > 0.3:
                    sample[secondary_symptom] = 1
            
            # Add some noise - occasionally include random symptoms (10% chance)
            for symptom in symptoms:
                if sample[symptom] == 0 and np.random.random() > 0.9:
                    sample[symptom] = 1
            
            # Add the condition label
            sample['condition'] = condition
            training_data.append(sample)
    
    # Create DataFrame
    df = pd.DataFrame(training_data)
    return df

def train_conversational_model():
    """Train the conversational AI model"""
    
    print("🤖 Creating conversational diagnosis training dataset...")
    df = create_conversational_dataset()
    
    print(f"📊 Dataset created with {len(df)} samples and {len(df['condition'].unique())} conditions")
    print(f"Conditions: {list(df['condition'].unique())}")
    
    # Prepare features and labels
    feature_columns = [col for col in df.columns if col != 'condition']
    X = df[feature_columns].values
    y = df['condition'].values
    
    print(f"🔬 Features: {len(feature_columns)} symptoms")
    print(f"Feature names: {feature_columns}")
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"📈 Training set: {len(X_train)} samples")
    print(f"📉 Testing set: {len(X_test)} samples")
    
    # Create and train the model
    print("🎯 Training Random Forest Classifier...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"✅ Model Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    
    # Print detailed classification report
    print("\n📋 Detailed Classification Report:")
    print(classification_report(y_test, y_pred))
    
    # Feature importance analysis
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n🔍 Top 10 Most Important Features:")
    print(feature_importance.head(10))
    
    # Create label encoder
    label_encoder = LabelEncoder()
    label_encoder.fit(y)
    
    # Create prescription mapping
    prescriptions_map = {
        'Common Cold': ['Rest', 'Drink fluids', 'Over-the-counter pain relievers'],
        'Flu': ['Antiviral medication', 'Rest', 'Drink fluids', 'Fever reducers'],
        'COVID-19': ['Isolation', 'Rest', 'Monitor symptoms', 'Seek medical care if severe'],
        'Pneumonia': ['Antibiotics', 'Rest', 'Hospitalization if severe'],
        'Bronchitis': ['Cough suppressants', 'Rest', 'Drink fluids'],
        'Sinusitis': ['Decongestants', 'Nasal irrigation', 'Antibiotics if bacterial'],
        'Migraine': ['Pain relievers', 'Rest in dark room', 'Avoid triggers'],
        'Tension Headache': ['Pain relievers', 'Stress management', 'Rest'],
        'Gastroenteritis': ['Rest', 'Clear fluids', 'BRAT diet', 'Rehydration'],
        'Allergic Rhinitis': ['Antihistamines', 'Avoid allergens', 'Nasal sprays']
    }
    
    # Save all model components
    print("\n💾 Saving conversational model components...")
    joblib.dump(model, 'conversational_diagnosis_model.pkl')
    joblib.dump(label_encoder, 'conversational_label_encoder.pkl')
    joblib.dump(feature_columns, 'conversational_feature_names.pkl')
    joblib.dump(prescriptions_map, 'conversational_prescriptions_map.pkl')
    
    print("✅ All model components saved successfully!")
    
    # Save training dataset for reference
    df.to_csv('conversational_training_dataset.csv', index=False)
    print("✅ Training dataset saved as conversational_training_dataset.csv")
    
    return {
        'model': model,
        'accuracy': accuracy,
        'feature_importance': feature_importance,
        'feature_names': feature_columns,
        'conditions': list(df['condition'].unique())
    }

if __name__ == "__main__":
    print("🚀 Starting Conversational AI Model Training...")
    results = train_conversational_model()
    print(f"\n🎉 Training completed! Final accuracy: {results['accuracy']*100:.2f}%")
