"""
Test script for Kuro AI Backend
Tests all endpoints and capabilities
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint"""
    print("\n" + "="*60)
    print("🔍 Testing Health Check...")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_kuro(message):
    """Test Kuro endpoint with a message"""
    print("\n" + "="*60)
    print(f"🤖 Testing Kuro with: '{message}'")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/kuro",
        json={"message": message}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Reply: {data.get('reply')}")
        print(f"Function Called: {data.get('function_called')}")
        print(f"Success: {data.get('success')}")
    else:
        print(f"❌ Error: {response.text}")
    
    return response.status_code == 200

def main():
    print("\n" + "="*60)
    print("🚀 KURO AI BACKEND TEST SUITE")
    print("="*60)
    
    # Test 1: Health Check
    if not test_health():
        print("\n❌ Health check failed! Is the backend running?")
        return
    
    # Test 2: Simple greeting
    test_kuro("hello")
    
    # Test 3: Open app
    test_kuro("open notepad")
    
    # Test 4: Tell joke
    test_kuro("tell me a joke")
    
    # Test 5: Memory save
    test_kuro("remember that I like coffee")
    
    # Test 6: Memory recall
    test_kuro("what do you know about me?")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)
    print("\nKuro is ready to use! 🎉")
    print("Open http://localhost:3000 to start using the frontend.\n")

if __name__ == "__main__":
    main()
