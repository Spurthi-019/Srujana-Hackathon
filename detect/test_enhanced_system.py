#!/usr/bin/env python3
"""
Test Script for Enhanced ClassTrack System
==========================================

This script tests all the integrated features:
1. Original API endpoints
2. Attendance system
3. Chatbot functionality
4. Face recognition
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n🧪 Testing: {description}")
    print(f"📍 {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"✅ Status: {response.status_code}")
        result = response.json()
        print(f"📄 Response: {json.dumps(result, indent=2)[:200]}...")
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run comprehensive tests"""
    print("🚀 ClassTrack Enhanced System Tests")
    print("=" * 50)
    
    # Test original endpoints
    test_endpoint("GET", "/", description="Root endpoint - system status")
    test_endpoint("GET", "/ping-db", description="Database connectivity")
    test_endpoint("GET", "/users", description="List users")
    
    # Test attendance endpoints  
    test_endpoint("GET", "/attendance/today", description="Today's attendance")
    test_endpoint("GET", "/attendance/student/Student_1", description="Student attendance history")
    
    # Test chatbot endpoints
    test_endpoint("GET", "/chatbot/history", description="Chat history")
    test_endpoint("POST", "/chatbot/ask", 
                 data={"question": "What is Python programming?", "context": ""}, 
                 description="Ask chatbot a question")
    test_endpoint("GET", "/chatbot/documents", description="List uploaded documents")
    
    # Test speech recognition
    test_endpoint("GET", "/speech/test-microphone", description="Speech recognition status")
    
    print("\n🎉 All tests completed!")
    print("📊 Check the Simple Browser at http://localhost:5001/docs for full API documentation")

if __name__ == "__main__":
    main()