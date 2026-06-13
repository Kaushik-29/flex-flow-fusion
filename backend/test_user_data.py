#!/usr/bin/env python3
"""
Test script for user registration, login, and data retrieval
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_user_flow():
    print("🧪 Testing User Registration & Login Flow")
    print("=" * 50)
    
    # Test user data with unique username
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_user = {
        "name": "John Doe",
        "username": f"johndoe_test_{timestamp}",
        "email": f"john.doe.test_{timestamp}@example.com",
        "password": "password123"
    }
    
    try:
        # Step 1: Register user
        print("\n1. Registering user...")
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        if response.status_code == 201:
            print("✅ User registered successfully")
        else:
            print(f"❌ Registration failed: {response.text}")
            return
            
        # Step 2: Login user
        print("\n2. Logging in user...")
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ User logged in successfully")
            print(f"✅ Token received: {token[:20]}...")
        else:
            print(f"❌ Login failed: {response.text}")
            return
            
        # Step 3: Get user data
        print("\n3. Getting user data...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print("✅ User data retrieved successfully")
            print(f"✅ Name: {user_data.get('name', 'NOT FOUND')}")
            print(f"✅ Username: {user_data.get('username', 'NOT FOUND')}")
            print(f"✅ Email: {user_data.get('email', 'NOT FOUND')}")
            
            # Check if name is present
            if user_data.get('name'):
                print("✅ Name field is present and correct!")
            else:
                print("❌ Name field is missing or empty!")
                return
                
        else:
            print(f"❌ Failed to get user data: {response.text}")
            return
            
        print("\n🎉 All tests passed!")
        print("✅ User registration works")
        print("✅ User login works")
        print("✅ User data retrieval works")
        print("✅ Name field is properly returned")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running on port 8000")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_user_flow() 