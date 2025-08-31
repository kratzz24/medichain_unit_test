import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

def train_enhanced_diagnosis_model():
    """Train the enhanced AI diagnosis model with new symptoms and conditions"""
    
    # Load the enhanced dataset
    print("Loading enhanced comprehensive dataset...")
    try:
        df = pd.read_csv('comprehensive_symptoms_dataset.csv')
        print(f"Successfully loaded dataset with {len(df)} samples and {len(df.columns)-1} symptoms")
    except FileNotFoundError:
        print("Error: comprehensive_symptoms_dataset.csv not found!")
        return None, None, None
    
    # Display dataset info
    print(f"Dataset shape: {df.shape}")
    print(f"Symptoms included: {list(df.columns[:-1])}")
    
    # Check for missing values
    if df.isnull().sum().sum() > 0:
        print("Warning: Dataset contains missing values!")
        df = df.dropna()
        print(f"After removing missing values: {len(df)} samples")
    
    # Drop classes with fewer than 2 samples (fix for stratify issue)
    class_counts = df['diagnosis'].value_counts()
    print(f"\nTotal classes in dataset: {len(class_counts)}")
    print(f"Class distribution:")
    print(class_counts.to_string())
    
    # Keep only classes with at least 2 samples for stratified splitting
    valid_classes = class_counts[class_counts >= 2].index
    df = df[df['diagnosis'].isin(valid_classes)]
    
    if df.empty:
        raise ValueError("Dataset has no valid classes with at least 2 samples.")
    
    print(f"\nAfter filtering, using {len(valid_classes)} classes with {len(df)} samples")
    
    # Separate features and target
    X = df.drop('diagnosis', axis=1)
    y = df['diagnosis']
    
    # Store feature names
    feature_names = X.columns.tolist()
    print(f"\nFeatures being used: {feature_names}")
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Check if we have enough samples for stratified split
    min_class_count = min(pd.Series(y_encoded).value_counts())
    num_classes = len(np.unique(y_encoded))
    test_size = 0.2
    
    # Calculate minimum samples needed for stratified split
    min_test_samples_needed = num_classes
    current_test_samples = int(len(df) * test_size)
    
    print(f"\nSplit Information:")
    print(f"Number of classes: {num_classes}")
    print(f"Total samples: {len(df)}")
    print(f"Proposed test samples: {current_test_samples}")
    print(f"Minimum test samples needed for stratified split: {min_test_samples_needed}")
    
    # Use simple random split for small datasets
    if current_test_samples < min_test_samples_needed:
        print("Not enough samples for stratified split. Using simple random split.")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=42
        )
    else:
        # Try stratified split with adjusted test size if needed
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
            )
            print("Using stratified split")
        except ValueError as e:
            print(f"Stratified split failed: {e}")
            print("Falling back to simple random split")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=test_size, random_state=42
            )
    
    # Train enhanced Random Forest model
    print("\nTraining enhanced Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'  # Handle class imbalance
    )
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Performance:")
    print(f"Enhanced Random Forest Accuracy: {accuracy:.2%}")
    
    print(f"\nClassification Report:")
    
    # Get the classes that are actually present in the test set
    unique_test_classes = np.unique(y_test)
    test_class_names = [label_encoder.classes_[i] for i in unique_test_classes]
    
    print(classification_report(y_test, y_pred, 
                              labels=unique_test_classes,
                              target_names=test_class_names,
                              zero_division=0))
    
    # Create confusion matrix
    cm = confusion_matrix(y_test, y_pred, labels=unique_test_classes)
    plt.figure(figsize=(14, 12))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=test_class_names,
                yticklabels=test_class_names)
    plt.title('Confusion Matrix - Enhanced Diagnosis Model (Random Forest)')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('enhanced_confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\nTop 10 Most Important Features:")
    print(feature_importance.head(10).to_string(index=False))
    
    plt.figure(figsize=(12, 8))
    sns.barplot(data=feature_importance, x='importance', y='feature')
    plt.title('Feature Importance - Enhanced Diagnosis Model (Random Forest)')
    plt.xlabel('Importance')
    plt.tight_layout()
    plt.savefig('enhanced_feature_importance.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Save enhanced model and encoders
    print("\nSaving enhanced model...")
    joblib.dump(model, 'enhanced_diagnosis_model.pkl')
    joblib.dump(label_encoder, 'enhanced_label_encoder.pkl')
    joblib.dump(feature_names, 'enhanced_feature_names.pkl')
    
    # Create enhanced prescriptions map based on training data
    print("Creating enhanced prescriptions map...")
    prescriptions_map = {}
    
    # Group by diagnosis and create prescription recommendations
    for diagnosis in label_encoder.classes_:
        diagnosis_data = df[df['diagnosis'] == diagnosis]
        dominant_symptoms = []
        
        # Find the most common symptoms for this diagnosis
        for symptom in feature_names:
            if diagnosis_data[symptom].mean() > 0.5:  # If symptom appears in >50% of cases
                dominant_symptoms.append(symptom)
        
        # Create prescription based on dominant symptoms
        if 'fever' in dominant_symptoms or 'body_aches' in dominant_symptoms:
            base_meds = ["Paracetamol", "Ibuprofen"]
        else:
            base_meds = []
            
        if 'cough' in dominant_symptoms:
            base_meds.extend(["Cough syrup", "Throat lozenges"])
            
        if 'nausea' in dominant_symptoms or 'diarrhea' in dominant_symptoms:
            base_meds.extend(["Oral rehydration solution", "Anti-nausea medication"])
            
        if 'headache' in dominant_symptoms:
            base_meds.extend(["Pain relievers", "Rest in dark room"])
            
        if 'shortness_of_breath' in dominant_symptoms:
            base_meds.extend(["Bronchodilator", "Seek immediate medical attention"])
            
        if 'chest_pain' in dominant_symptoms:
            base_meds.extend(["Seek immediate medical attention", "Cardiac evaluation"])
            
        # Add general recommendations
        general_recommendations = ["Rest", "Hydration", "Monitor symptoms"]
        
        prescriptions_map[diagnosis] = {
            'medications': list(set(base_meds)) if base_meds else ["Supportive care"],
            'recommendations': general_recommendations,
            'follow_up': "Consult healthcare provider if symptoms worsen"
        }
    
    # Save prescriptions map
    joblib.dump(prescriptions_map, 'enhanced_prescriptions_map.pkl')
    
    # Create a model info file
    model_info = {
        'model_type': 'Random Forest',
        'accuracy': float(accuracy),
        'num_features': len(feature_names),
        'num_classes': num_classes,
        'feature_names': feature_names,
        'class_names': label_encoder.classes_.tolist(),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'top_features': feature_importance.head(5).to_dict('records')
    }
    
    import json
    with open('enhanced_model_info.json', 'w') as f:
        json.dump(model_info, f, indent=2)
    
    print(f"\nEnhanced model training completed!")
    print(f"Model saved as: enhanced_diagnosis_model.pkl")
    print(f"Label encoder saved as: enhanced_label_encoder.pkl")
    print(f"Feature names saved as: enhanced_feature_names.pkl")
    print(f"Prescriptions map saved as: enhanced_prescriptions_map.pkl")
    print(f"Model info saved as: enhanced_model_info.json")
    print(f"\nFinal Model Performance: {accuracy:.2%}")
    
    return model, label_encoder, feature_names

if __name__ == "__main__":
    train_enhanced_diagnosis_model()
