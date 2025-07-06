#!/usr/bin/env python3
"""
Test script to verify points endpoints are working
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_points_endpoints():
    """Test the points endpoints"""
    
    print("Testing Points Endpoints...")
    print("=" * 50)
    
    # Test 1: Check if points router is accessible
    try:
        response = requests.get(f"{BASE_URL}/points/config")
        print(f"✅ Points config endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Points config endpoint failed: {e}")
    
    # Test 2: Check if user points endpoint exists (will return 401 without auth)
    try:
        response = requests.get(f"{BASE_URL}/points/user")
        print(f"✅ Points user endpoint: {response.status_code}")
        if response.status_code == 401:
            print("   Expected 401 (authentication required)")
    except Exception as e:
        print(f"❌ Points user endpoint failed: {e}")
    
    # Test 3: Check if leaderboard endpoint exists
    try:
        response = requests.get(f"{BASE_URL}/points/leaderboard")
        print(f"✅ Points leaderboard endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Points leaderboard endpoint failed: {e}")
    
    # Test 4: Check if friends endpoint exists (will return 401 without auth)
    try:
        response = requests.get(f"{BASE_URL}/points/friends")
        print(f"✅ Points friends endpoint: {response.status_code}")
        if response.status_code == 401:
            print("   Expected 401 (authentication required)")
    except Exception as e:
        print(f"❌ Points friends endpoint failed: {e}")
    
    print("\n" + "=" * 50)
    print("Points endpoints test completed!")

if __name__ == "__main__":
    test_points_endpoints() 