"""
Test script to verify the top 3 predictions with medications are working correctly
"""

import requests
import json

def test_top3_predictions():
    """Test the enhanced AI server for top 3 predictions with medications"""
    
    url = "http://localhost:5001/diagnose"
    
    # Test data
    test_data = {
        "symptoms": {
            "symptomText": "I have a severe headache, fever, and nausea. I feel dizzy and my neck feels stiff."
        },
        "patient_data": {
            "age": 25,
            "gender": "female",
            "patient_id": "test_123",
            "name": "Test Patient"
        },
        "doctor_id": None,
        "include_recommendations": True,
        "detailed_analysis": True,
        "save_to_database": False,
        "session_type": "guest"
    }
    
    try:
        print("🧪 Testing Enhanced AI Server - Top 3 Predictions with Medications")
        print("="*70)
        
        response = requests.post(url, json=test_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Server Response: SUCCESS")
            print(f"📊 Response Status: {result.get('success', 'Unknown')}")
            
            if result.get('success') and 'data' in result:
                data = result['data']
                
                print(f"\n🎯 Primary Diagnosis: {data.get('diagnosis', 'Not available')}")
                print(f"📈 Confidence: {data.get('confidence', 0):.1f}%")
                
                # Check top predictions
                if 'top_predictions' in data:
                    top_predictions = data['top_predictions']
                    print(f"\n🏆 Top {len(top_predictions)} Predictions:")
                    print("-" * 50)
                    
                    for i, prediction in enumerate(top_predictions, 1):
                        print(f"\n#{i} - {prediction.get('diagnosis', 'Unknown').replace('_', ' ').title()}")
                        print(f"   Confidence: {prediction.get('confidence', 0):.1f}%")
                        
                        # Check medications
                        if 'medications' in prediction and prediction['medications']:
                            print(f"   💊 Medications: {', '.join(prediction['medications'])}")
                            if 'dosage' in prediction:
                                print(f"   📋 Dosage: {prediction.get('dosage', 'Not specified')}")
                            if 'duration' in prediction:
                                print(f"   ⏰ Duration: {prediction.get('duration', 'Not specified')}")
                            if 'instructions' in prediction:
                                print(f"   📝 Instructions: {prediction.get('instructions', 'Not specified')}")
                        else:
                            print("   💊 No specific medications available")
                else:
                    print("\n❌ No top_predictions found in response")
                
                # Check conversational response
                if 'conversational_response' in data:
                    conv_response = data['conversational_response']
                    print(f"\n💬 Conversational Response Available: {len(conv_response)} characters")
                
                print("\n" + "="*70)
                print("✅ TEST COMPLETED SUCCESSFULLY")
                
            else:
                print(f"❌ Error in response: {result.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ Server Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to AI server on port 5001")
        print("   Make sure the enhanced_confident_ai_server.py is running")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_top3_predictions()
