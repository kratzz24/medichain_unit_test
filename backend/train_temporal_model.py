import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

def train_temporal_diagnosis_model():
    """Train the temporal-enhanced AI diagnosis model with duration information"""
    
    # Load the temporal dataset
    print("Loading temporal-enhanced dataset...")
    try:
        df = pd.read_csv('temporal_symptoms_dataset.csv')
        print(f"Successfully loaded dataset with {len(df)} samples and {len(df.columns)-1} features")
    except FileNotFoundError:
        print("Error: temporal_symptoms_dataset.csv not found!")
        return None, None, None
    
    # Display dataset info
    print(f"Dataset shape: {df.shape}")
    print(f"Features included: {list(df.columns[:-1])}")
    
    # Check for missing values
    if df.isnull().sum().sum() > 0:
        print("Warning: Dataset contains missing values!")
        df = df.dropna()
        print(f"After removing missing values: {len(df)} samples")
    
    # Drop classes with fewer than 2 samples
    class_counts = df['diagnosis'].value_counts()
    print(f"\nTotal classes in dataset: {len(class_counts)}")
    print(f"Class distribution:")
    print(class_counts.to_string())
    
    # Keep only classes with at least 2 samples
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
    
    # Split data
    test_size = 0.2
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=test_size, random_state=42
    )
    
    # Train temporal-enhanced Random Forest model
    print("\nTraining temporal-enhanced Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=250,
        max_depth=18,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1,
        class_weight='balanced'
    )
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nTemporal Model Performance:")
    print(f"Enhanced Random Forest Accuracy: {accuracy:.2%}")
    
    # Feature importance analysis
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\nTop 15 Most Important Features (including duration):")
    print(feature_importance.head(15).to_string(index=False))
    
    # Separate temporal features analysis
    duration_features = [f for f in feature_names if '_duration' in f]
    symptom_features = [f for f in feature_names if '_duration' not in f]
    
    duration_importance = feature_importance[feature_importance['feature'].isin(duration_features)]
    symptom_importance = feature_importance[feature_importance['feature'].isin(symptom_features)]
    
    print(f"\nDuration Features Importance:")
    print(duration_importance.to_string(index=False))
    
    # Create comprehensive visualization
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Overall feature importance
    plt.subplot(2, 2, 1)
    top_features = feature_importance.head(15)
    colors = ['red' if '_duration' in f else 'blue' for f in top_features['feature']]
    plt.barh(range(len(top_features)), top_features['importance'], color=colors)
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('Importance')
    plt.title('Top 15 Feature Importance (Red=Duration, Blue=Symptom)')
    plt.gca().invert_yaxis()
    
    # Plot 2: Duration vs Symptom importance comparison
    plt.subplot(2, 2, 2)
    duration_avg = duration_importance['importance'].mean() if not duration_importance.empty else 0
    symptom_avg = symptom_importance['importance'].mean()
    plt.bar(['Duration Features', 'Symptom Features'], [duration_avg, symptom_avg], 
            color=['red', 'blue'], alpha=0.7)
    plt.ylabel('Average Importance')
    plt.title('Duration vs Symptom Features Average Importance')
    
    # Plot 3: Confusion Matrix (top classes only)
    plt.subplot(2, 2, 3)
    unique_test_classes = np.unique(y_test)
    test_class_names = [label_encoder.classes_[i] for i in unique_test_classes]
    cm = confusion_matrix(y_test, y_pred, labels=unique_test_classes)
    
    # Show only if not too many classes
    if len(unique_test_classes) <= 10:
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                    xticklabels=test_class_names, yticklabels=test_class_names,
                    cbar=False)
        plt.title('Confusion Matrix')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
    else:
        plt.text(0.5, 0.5, f'Too many classes ({len(unique_test_classes)}) to display', 
                ha='center', va='center', transform=plt.gca().transAxes)
        plt.title('Confusion Matrix (Too many classes)')
    
    # Plot 4: Duration feature comparison
    plt.subplot(2, 2, 4)
    if not duration_importance.empty:
        duration_importance_sorted = duration_importance.sort_values('importance', ascending=True)
        plt.barh(range(len(duration_importance_sorted)), duration_importance_sorted['importance'], color='red', alpha=0.7)
        plt.yticks(range(len(duration_importance_sorted)), 
                  [f.replace('_duration', '') for f in duration_importance_sorted['feature']])
        plt.xlabel('Importance')
        plt.title('Duration Features Importance')
    else:
        plt.text(0.5, 0.5, 'No duration features found', ha='center', va='center', transform=plt.gca().transAxes)
    
    plt.tight_layout()
    plt.savefig('temporal_model_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Save temporal model and encoders
    print("\nSaving temporal-enhanced model...")
    joblib.dump(model, 'temporal_diagnosis_model.pkl')
    joblib.dump(label_encoder, 'temporal_label_encoder.pkl')
    joblib.dump(feature_names, 'temporal_feature_names.pkl')
    
    # Create enhanced prescriptions map with duration consideration
    print("Creating temporal-enhanced prescriptions map...")
    prescriptions_map = {}
    
    for diagnosis in label_encoder.classes_:
        diagnosis_data = df[df['diagnosis'] == diagnosis]
        
        # Analyze symptom patterns and durations
        symptom_analysis = {}
        duration_analysis = {}
        
        for feature in feature_names:
            if '_duration' in feature:
                avg_duration = diagnosis_data[feature].mean()
                if avg_duration > 0:
                    duration_analysis[feature.replace('_duration', '')] = int(avg_duration)
            else:
                prevalence = diagnosis_data[feature].mean()
                if prevalence > 0.3:  # If symptom appears in >30% of cases
                    symptom_analysis[feature] = prevalence
        
        # Create temporal-aware recommendations
        medications = []
        recommendations = []
        urgency_level = "Normal"
        
        # Analyze critical symptoms and their durations
        if 'fever' in symptom_analysis:
            fever_duration = duration_analysis.get('fever', 0)
            if fever_duration > 7:
                medications.extend(["Paracetamol", "Seek medical attention"])
                urgency_level = "High"
            elif fever_duration > 3:
                medications.extend(["Paracetamol", "Monitor closely"])
            else:
                medications.append("Paracetamol")
        
        if 'cough' in symptom_analysis:
            cough_duration = duration_analysis.get('cough', 0)
            if cough_duration > 14:
                medications.extend(["Cough suppressant", "Chest X-ray recommended"])
                urgency_level = "High"
            elif cough_duration > 7:
                medications.extend(["Cough syrup", "Monitor"])
            else:
                medications.append("Throat lozenges")
        
        if 'headache' in symptom_analysis:
            headache_duration = duration_analysis.get('headache', 0)
            if headache_duration > 7:
                medications.extend(["Pain relievers", "Neurological evaluation"])
                urgency_level = "High"
            else:
                medications.append("Pain relievers")
        
        if 'fatigue' in symptom_analysis:
            fatigue_duration = duration_analysis.get('fatigue', 0)
            if fatigue_duration > 30:
                recommendations.extend(["Complete blood work", "Specialist consultation"])
                urgency_level = "High"
            elif fatigue_duration > 14:
                recommendations.append("Rest and nutrition assessment")
        
        # Add duration-specific recommendations
        if any(d > 14 for d in duration_analysis.values()):
            recommendations.append("Symptoms persisting >2 weeks require medical evaluation")
        
        if any(d > 30 for d in duration_analysis.values()):
            recommendations.append("Chronic symptoms (>1 month) need specialist care")
            urgency_level = "High"
        
        # Default recommendations
        if not medications:
            medications = ["Supportive care"]
        
        recommendations.extend(["Rest", "Hydration", "Monitor symptoms"])
        
        prescriptions_map[diagnosis] = {
            'medications': list(set(medications)),
            'recommendations': list(set(recommendations)),
            'urgency_level': urgency_level,
            'typical_durations': duration_analysis,
            'follow_up': "Consult healthcare provider if symptoms worsen or persist beyond expected duration"
        }
    
    # Save temporal prescriptions map
    joblib.dump(prescriptions_map, 'temporal_prescriptions_map.pkl')
    
    # Create model info
    model_info = {
        'model_type': 'Temporal Random Forest',
        'accuracy': float(accuracy),
        'num_features': len(feature_names),
        'num_classes': len(valid_classes),
        'feature_names': feature_names,
        'class_names': label_encoder.classes_.tolist(),
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'duration_features': duration_features,
        'symptom_features': symptom_features,
        'duration_importance_avg': float(duration_avg),
        'symptom_importance_avg': float(symptom_avg),
        'top_features': feature_importance.head(10).to_dict('records')
    }
    
    import json
    with open('temporal_model_info.json', 'w') as f:
        json.dump(model_info, f, indent=2)
    
    print(f"\nTemporal-enhanced model training completed!")
    print(f"Model saved as: temporal_diagnosis_model.pkl")
    print(f"Label encoder saved as: temporal_label_encoder.pkl")
    print(f"Feature names saved as: temporal_feature_names.pkl")
    print(f"Temporal prescriptions map saved as: temporal_prescriptions_map.pkl")
    print(f"Model info saved as: temporal_model_info.json")
    print(f"\nFinal Model Performance: {accuracy:.2%}")
    print(f"Duration features average importance: {duration_avg:.4f}")
    print(f"Symptom features average importance: {symptom_avg:.4f}")
    
    return model, label_encoder, feature_names

if __name__ == "__main__":
    train_temporal_diagnosis_model()
