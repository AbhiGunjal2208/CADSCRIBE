#!/usr/bin/env python3
"""
Simple API test script.
"""
import requests
import json
import time

def test_api_endpoints():
    """Test the FastAPI endpoints."""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing FastAPI Endpoints...")
    
    # Test 1: Basic health check
    try:
        print("\n1️⃣ Testing basic health check...")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            print(f"📊 Service: {data['service']}")
            print(f"🗄️  Database: {data['database']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Detailed health check
    try:
        print("\n2️⃣ Testing detailed health check...")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Detailed health check passed")
            print(f"📊 Services status: {data['services']}")
            print(f"🔧 Environment: {data['environment']}")
        else:
            print(f"❌ Detailed health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Detailed health check error: {e}")
    
    # Test 3: User signup
    try:
        print("\n3️⃣ Testing user signup...")
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "testpassword123"
        }
        response = requests.post(f"{base_url}/auth/signup", json=user_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User signup successful")
            print(f"👤 User: {data['user']['name']} ({data['user']['email']})")
            print(f"🔑 Token type: {data['token_type']}")
            return data['access_token']
        else:
            print(f"❌ User signup failed: {response.status_code}")
            print(f"📝 Response: {response.text}")
    except Exception as e:
        print(f"❌ User signup error: {e}")
    
    return None

def test_authenticated_endpoints(token):
    """Test endpoints that require authentication."""
    base_url = "http://localhost:8000"
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔐 Testing authenticated endpoints...")
    
    # Test 4: Get current user
    try:
        print("\n4️⃣ Testing get current user...")
        response = requests.get(f"{base_url}/auth/me", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Get current user successful")
            print(f"👤 User: {data['name']} ({data['email']})")
        else:
            print(f"❌ Get current user failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Get current user error: {e}")
    
    # Test 5: Generate CAD model
    try:
        print("\n5️⃣ Testing CAD model generation...")
        model_data = {
            "description": "Create a simple cube",
            "output_format": "stl",
            "parameters": {"size": 10}
        }
        response = requests.post(f"{base_url}/models/generate", json=model_data, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ CAD model generation successful")
            print(f"📦 Model ID: {data['id']}")
            print(f"📄 Title: {data['title']}")
            print(f"📁 Format: {data['format']}")
            print(f"🔗 Download URL: {data['download_url']}")
        else:
            print(f"❌ CAD model generation failed: {response.status_code}")
            print(f"📝 Response: {response.text}")
    except Exception as e:
        print(f"❌ CAD model generation error: {e}")
    
    # Test 6: AI chat
    try:
        print("\n6️⃣ Testing AI chat...")
        chat_data = {
            "message": "Hello, can you help me create a cylinder?",
            "project_id": "test_project"
        }
        response = requests.post(f"{base_url}/ai/chat", json=chat_data, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI chat successful")
            print(f"💬 Response: {data['message']['content'][:100]}...")
            if data.get('code_generated'):
                print(f"💻 Code generated: {len(data['code_generated'])} characters")
        else:
            print(f"❌ AI chat failed: {response.status_code}")
            print(f"📝 Response: {response.text}")
    except Exception as e:
        print(f"❌ AI chat error: {e}")

if __name__ == "__main__":
    print("🚀 Starting API Tests...")
    print("⚠️  Make sure the FastAPI server is running on http://localhost:8000")
    print("   Start it with: uvicorn main:app --reload --port 8000")
    print()
    
    # Wait a moment for user to start server if needed
    input("Press Enter when the server is running...")
    
    # Test basic endpoints
    token = test_api_endpoints()
    
    # Test authenticated endpoints if we got a token
    if token:
        test_authenticated_endpoints(token)
    
    print("\n🎉 API testing completed!")

