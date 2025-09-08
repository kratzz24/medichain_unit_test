#!/usr/bin/env python3
"""
Test script for the Enhanced Confident AI Server
"""

import requests
import json
import time

def test_server():
    """Test the enhanced confident AI server"""
    
    print("🧪 Testing Enhanced Confident AI Server")
    print("="*50)
    
    base_url = "http://localhost:5001"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Health Check: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"  Status: {health_data['status']}")
            print(f"  AI System: {health_data['ai_system']}")
            print(f"  Confidence Booster: {health_data['confidence_booster']}")
        
        # Test diagnosis endpoint
        diagnosis_data = {
            "symptoms": "severe headache and fever for 3 days, feeling very tired"
        }
        
        response = requests.post(f"{base_url}/diagnose", json=diagnosis_data)
        print(f"\nDiagnosis Request: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  Diagnosis: {result['primary_diagnosis']}")
            print(f"  Confidence: {result['confidence']:.1f}%")
            print(f"  Base Confidence: {result['base_confidence']:.1f}%")
            print(f"  Confidence Level: {result['confidence_level']}")
            print(f"  Boost Applied: {result['enhancement_info']['boost_applied']}")
            print(f"  Boost Percentage: {result['enhancement_info']['boost_percentage']:.1f}%")
            print(f"  Boost Factors: {result['enhancement_info']['boost_factors_count']}")
            
            # Verify percentage format
            assert 0 <= result['confidence'] <= 100, "Confidence not in percentage range!"
            assert 0 <= result['base_confidence'] <= 100, "Base confidence not in percentage range!"
            
            print("\n✅ Server response with proper percentage format!")
            return True
        else:
            print(f"  Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on port 5001")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    if success:
        print("\n🎉 Server percentage confidence fix verified!")
    else:
        print("\n💥 Server test failed!")
