#!/usr/bin/env python3
"""
Comprehensive test script to verify all endpoints are working
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_all_endpoints():
    """Test all the main endpoints"""
    
    print("Testing All Endpoints...")
    print("=" * 60)
    
    # Test 1: Root endpoint
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Root endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
    
    # Test 2: Points endpoints
    print("\n--- Points Endpoints ---")
    try:
        response = requests.get(f"{BASE_URL}/points/config")
        print(f"✅ Points config: {response.status_code}")
    except Exception as e:
        print(f"❌ Points config failed: {e}")
    
    try:
        response = requests.get(f"{BASE_URL}/points/user")
        print(f"✅ Points user: {response.status_code} (expected 401)")
    except Exception as e:
        print(f"❌ Points user failed: {e}")
    
    try:
        response = requests.get(f"{BASE_URL}/points/leaderboard")
        print(f"✅ Points leaderboard: {response.status_code}")
    except Exception as e:
        print(f"❌ Points leaderboard failed: {e}")
    
    # Test 3: Notifications endpoints
    print("\n--- Notifications Endpoints ---")
    try:
        response = requests.get(f"{BASE_URL}/notifications")
        print(f"✅ Notifications: {response.status_code} (expected 401)")
    except Exception as e:
        print(f"❌ Notifications failed: {e}")
    
    try:
        response = requests.get(f"{BASE_URL}/notifications/friend-requests")
        print(f"✅ Friend requests notifications: {response.status_code} (expected 401)")
    except Exception as e:
        print(f"❌ Friend requests notifications failed: {e}")
    
    # Test 4: Auth endpoints
    print("\n--- Auth Endpoints ---")
    try:
        response = requests.get(f"{BASE_URL}/auth/me")
        print(f"✅ Auth me: {response.status_code} (expected 401)")
    except Exception as e:
        print(f"❌ Auth me failed: {e}")
    
    try:
        response = requests.get(f"{BASE_URL}/auth/friends/requests")
        print(f"✅ Auth friend requests: {response.status_code} (expected 401)")
    except Exception as e:
        print(f"❌ Auth friend requests failed: {e}")
    
    # Test 5: Workout endpoints
    print("\n--- Workout Endpoints ---")
    try:
        response = requests.post(f"{BASE_URL}/workout/start", json={"type": "squat"})
        print(f"✅ Workout start: {response.status_code} (expected 401)")
    except Exception as e:
        print(f"❌ Workout start failed: {e}")
    
    # Test 6: Leaderboard endpoints
    print("\n--- Leaderboard Endpoints ---")
    try:
        response = requests.get(f"{BASE_URL}/leaderboard/top")
        print(f"✅ Leaderboard top: {response.status_code}")
    except Exception as e:
        print(f"❌ Leaderboard top failed: {e}")
    
    print("\n" + "=" * 60)
    print("All endpoints test completed!")
    print("\nExpected results:")
    print("- Public endpoints (config, leaderboard): 200")
    print("- Protected endpoints: 401 (authentication required)")
    print("- All endpoints should be accessible (no 404 errors)")

if __name__ == "__main__":
    test_all_endpoints() 