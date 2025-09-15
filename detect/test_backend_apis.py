import requests
import time
import subprocess
import sys
import threading
from pathlib import Path

def test_backend_endpoints():
    """Test all backend API endpoints"""
    base_url = "http://localhost:5001"
    
    endpoints_to_test = [
        {"url": f"{base_url}/", "method": "GET", "description": "Root endpoint"},
        {"url": f"{base_url}/health", "method": "GET", "description": "Health check"},
        {"url": f"{base_url}/api/students", "method": "GET", "description": "Get students"},
        {"url": f"{base_url}/api/faculty", "method": "GET", "description": "Get faculty"},
        {"url": f"{base_url}/api/classes", "method": "GET", "description": "Get classes"},
    ]
    
    print("🧪 Testing Backend API Endpoints...")
    
    for endpoint in endpoints_to_test:
        try:
            print(f"\n📡 Testing {endpoint['description']}: {endpoint['url']}")
            
            response = requests.get(endpoint['url'], timeout=5)
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: {response.status_code}")
                print(f"   Response: {response.json()}")
            else:
                print(f"⚠️  WARNING: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ CONNECTION ERROR: Backend not running on {endpoint['url']}")
            return False
        except requests.exceptions.Timeout:
            print(f"❌ TIMEOUT: {endpoint['url']} took too long to respond")
            return False
        except Exception as e:
            print(f"❌ ERROR: {e}")
            return False
    
    print(f"\n🎉 All backend endpoints tested!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Backend API Tests...")
    
    # Test endpoints
    success = test_backend_endpoints()
    
    if success:
        print("\n✅ Backend API is working correctly!")
    else:
        print("\n❌ Backend API has issues!")
        sys.exit(1)