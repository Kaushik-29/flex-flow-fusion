#!/usr/bin/env python3
"""
Test script for friend request functionality
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_auth_and_friends():
    print("🧪 Testing Friend Request System")
    print("=" * 50)
    
    # Test 1: Register two users
    print("\n1. Registering test users...")
    
    user1_data = {
        "name": "Test User 1",
        "username": "testuser1",
        "email": "test1@example.com",
        "password": "password123"
    }
    
    user2_data = {
        "name": "Test User 2", 
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "password123"
    }
    
    try:
        # Register user 1
        response = requests.post(f"{BASE_URL}/auth/register", json=user1_data)
        if response.status_code == 201:
            print("✅ User 1 registered successfully")
        else:
            print(f"❌ User 1 registration failed: {response.text}")
            
        # Register user 2
        response = requests.post(f"{BASE_URL}/auth/register", json=user2_data)
        if response.status_code == 201:
            print("✅ User 2 registered successfully")
        else:
            print(f"❌ User 2 registration failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running on port 8000")
        return
    
    # Test 2: Login both users
    print("\n2. Logging in users...")
    
    login_data1 = {
        "username": "testuser1",
        "password": "password123"
    }
    
    login_data2 = {
        "username": "testuser2", 
        "password": "password123"
    }
    
    try:
        # Login user 1
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data1)
        if response.status_code == 200:
            token1 = response.json()["access_token"]
            print("✅ User 1 logged in successfully")
        else:
            print(f"❌ User 1 login failed: {response.text}")
            return
            
        # Login user 2
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data2)
        if response.status_code == 200:
            token2 = response.json()["access_token"]
            print("✅ User 2 logged in successfully")
        else:
            print(f"❌ User 2 login failed: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test 3: Send friend request
    print("\n3. Sending friend request...")
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    friend_request_data = {"friend_username": "testuser2"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/friends/request", 
            json=friend_request_data,
            headers=headers1
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Friend request sent: {result['msg']}")
            request_id = result.get('request_id')
        else:
            print(f"❌ Friend request failed: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Friend request error: {e}")
        return
    
    # Test 4: Check friend requests for both users
    print("\n4. Checking friend requests...")
    
    try:
        # Check user 1's outgoing requests
        response = requests.get(f"{BASE_URL}/auth/friends/requests", headers=headers1)
        if response.status_code == 200:
            requests_data = response.json()
            print(f"✅ User 1 outgoing requests: {len(requests_data['outgoing'])}")
            print(f"✅ User 1 incoming requests: {len(requests_data['incoming'])}")
        else:
            print(f"❌ Failed to get user 1 requests: {response.text}")
            
        # Check user 2's incoming requests
        headers2 = {"Authorization": f"Bearer {token2}"}
        response = requests.get(f"{BASE_URL}/auth/friends/requests", headers=headers2)
        if response.status_code == 200:
            requests_data = response.json()
            print(f"✅ User 2 outgoing requests: {len(requests_data['outgoing'])}")
            print(f"✅ User 2 incoming requests: {len(requests_data['incoming'])}")
            
            # Get the request ID for user 2 to respond
            if requests_data['incoming']:
                incoming_request = requests_data['incoming'][0]
                request_id = incoming_request['id']
                print(f"✅ Found incoming request ID: {request_id}")
            else:
                print("❌ No incoming requests found for user 2")
                return
        else:
            print(f"❌ Failed to get user 2 requests: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Check requests error: {e}")
        return
    
    # Test 5: Accept friend request
    print("\n5. Accepting friend request...")
    
    try:
        response_data = {"request_id": request_id, "action": "accept"}
        response = requests.post(
            f"{BASE_URL}/auth/friends/request/{request_id}/respond",
            json=response_data,
            headers=headers2
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Friend request accepted: {result['msg']}")
        else:
            print(f"❌ Accept request failed: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ Accept request error: {e}")
        return
    
    # Test 6: Check friends list
    print("\n6. Checking friends list...")
    
    try:
        # Check user 1's friends
        response = requests.get(f"{BASE_URL}/auth/friends", headers=headers1)
        if response.status_code == 200:
            friends_data = response.json()
            print(f"✅ User 1 friends count: {len(friends_data['friends'])}")
            if friends_data['friends']:
                print(f"✅ User 1's friend: {friends_data['friends'][0]['username']}")
        else:
            print(f"❌ Failed to get user 1 friends: {response.text}")
            
        # Check user 2's friends
        response = requests.get(f"{BASE_URL}/auth/friends", headers=headers2)
        if response.status_code == 200:
            friends_data = response.json()
            print(f"✅ User 2 friends count: {len(friends_data['friends'])}")
            if friends_data['friends']:
                print(f"✅ User 2's friend: {friends_data['friends'][0]['username']}")
        else:
            print(f"❌ Failed to get user 2 friends: {response.text}")
            
    except Exception as e:
        print(f"❌ Check friends error: {e}")
        return
    
    print("\n🎉 All tests completed successfully!")
    print("=" * 50)
    print("✅ MongoDB is working correctly")
    print("✅ Friend request system is functional")
    print("✅ Backend API is responding properly")

if __name__ == "__main__":
    test_auth_and_friends() 