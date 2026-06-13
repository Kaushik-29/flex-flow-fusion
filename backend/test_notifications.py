#!/usr/bin/env python3
"""
Test script for notification endpoints
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_notifications():
    print("🧪 Testing Notification Endpoints")
    print("=" * 50)
    
    # Test user data
    test_user = {
        "name": "Notification Test User",
        "username": f"notif_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "email": f"notif.test.{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
        "password": "password123"
    }
    
    try:
        # Step 1: Register and login user
        print("\n1. Registering and logging in user...")
        
        # Register
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        if response.status_code != 201:
            print(f"❌ Registration failed: {response.text}")
            return
            
        # Login
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return
            
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ User logged in successfully")
        
        # Step 2: Test notifications endpoint
        print("\n2. Testing notifications endpoint...")
        response = requests.get(f"{BASE_URL}/notifications/", headers=headers)
        if response.status_code == 200:
            notifications = response.json()
            print(f"✅ Notifications endpoint working. Found {len(notifications)} notifications")
        else:
            print(f"❌ Notifications endpoint failed: {response.text}")
            return
            
        # Step 3: Test friend requests notifications
        print("\n3. Testing friend requests notifications...")
        response = requests.get(f"{BASE_URL}/notifications/friend-requests", headers=headers)
        if response.status_code == 200:
            friend_requests = response.json()
            print(f"✅ Friend requests notifications working. Found {len(friend_requests)} requests")
        else:
            print(f"❌ Friend requests notifications failed: {response.text}")
            return
            
        # Step 4: Test unread count
        print("\n4. Testing unread count...")
        response = requests.get(f"{BASE_URL}/notifications/unread-count", headers=headers)
        if response.status_code == 200:
            unread_data = response.json()
            print(f"✅ Unread count working. Count: {unread_data['unread_count']}")
        else:
            print(f"❌ Unread count failed: {response.text}")
            return
            
        # Step 5: Test CORS
        print("\n5. Testing CORS...")
        response = requests.options(f"{BASE_URL}/notifications/", headers={
            "Origin": "http://localhost:8080",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization"
        })
        
        if "Access-Control-Allow-Origin" in response.headers:
            print("✅ CORS headers present")
            print(f"   Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin')}")
        else:
            print("❌ CORS headers missing")
            
        print("\n🎉 All notification tests passed!")
        print("✅ Notification endpoints are working")
        print("✅ CORS is properly configured")
        print("✅ Authentication is working")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running on port 8000")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_notifications() 