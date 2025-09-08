#!/usr/bin/env python3
"""
Test script to verify percentage confidence fix
"""

from comprehensive_ai_diagnosis import ComprehensiveAIDiagnosis
import json

def test_percentage_confidence():
    """Test that confidence values are returned as proper percentages"""
    
    print("🧪 Testing Percentage Confidence Fix")
    print("="*50)
    
    try:
        # Initialize diagnosis system
        ai_diagnosis = ComprehensiveAIDiagnosis()
        
        # Test case
        symptoms = "severe headache and fever for 3 days, feeling very tired"
        result = ai_diagnosis.diagnose(symptoms)
        
        print(f"Input: {symptoms}")
        print(f"Diagnosis: {result['primary_diagnosis']}")
        print(f"Confidence: {result['confidence']:.1f}%")
        print(f"Base Confidence: {result['base_confidence']:.1f}%")
        print(f"Confidence Level: {result['confidence_level']}")
        
        print("\nTop 3 Predictions:")
        for i, pred in enumerate(result['top_predictions']):
            print(f"  {i+1}. {pred['diagnosis']}: {pred['confidence']:.1f}%")
        
        # Verify percentage range
        assert 0 <= result['confidence'] <= 100, f"Confidence {result['confidence']} not in percentage range!"
        assert 0 <= result['base_confidence'] <= 100, f"Base confidence {result['base_confidence']} not in percentage range!"
        
        for pred in result['top_predictions']:
            assert 0 <= pred['confidence'] <= 100, f"Prediction confidence {pred['confidence']} not in percentage range!"
        
        print("\n✅ All confidence values are properly in percentage format (0-100%)!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_percentage_confidence()
    if success:
        print("\n🎉 Percentage confidence fix verified successfully!")
    else:
        print("\n💥 Percentage confidence fix needs more work!")
