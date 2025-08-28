"""
Test script for the symptom parser
"""
from symptom_parser import SymptomParser

def test_symptom_parser():
    """Test the symptom parser with various inputs"""
    
    # Initialize parser
    parser = SymptomParser()
    
    # Test cases to evaluate
    test_cases = [
        "I have a high fever and persistent cough",
        "Feeling really tired, with headache and sore throat",
        "Shortness of breath when I try to climb stairs",
        "I have fever, cough, and feeling really tired",
        "My head is pounding, and I have a scratchy throat",
        "I've been coughing a lot and feel exhausted",
        "Severe headache with fever",
        "I'm experiencing trouble breathing and fatigue",
        "High fever, cough, and headache",
        "Bad sore throat with fever"
    ]
    
    # Process each test case
    for idx, text in enumerate(test_cases):
        print(f"\nTest Case #{idx+1}: '{text}'")
        
        # Parse symptoms
        symptoms = parser.parse_symptoms(text)
        print("Detected symptoms:")
        for feature, value in symptoms.items():
            if value > 0:
                print(f"  - {feature}: {value}")
        
        # Get feature vector
        vector = parser.get_feature_vector(text)
        print(f"Feature vector: {vector}")
        
        # Get symptom list
        symptom_list = parser.extract_symptoms_as_list(text)
        print(f"Symptom list: {symptom_list}")
        
    print("\nTesting complete!")

if __name__ == "__main__":
    test_symptom_parser()
