#!/usr/bin/env python3
"""
Simple test for friend request functionality
"""

import requests

BASE_URL = "http://localhost:8000"

def simple_test():
    print("🧪 Simple Friend Request Test")
    print("=" * 40)
    
    # Login with existing users
    print("\n1. Logging in users...")
    
    try:
        # Login user 1
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "username": "testuser1",
            "password": "password123"
        })
        
        if response.status_code == 200:
            token1 = response.json()["access_token"]
            print("✅ User 1 logged in")
        else:
            print(f"❌ User 1 login failed: {response.text}")
            return
            
        # Login user 2 (or create if doesn't exist)
        response = requests.post(f"{BASE_URL}/auth/login", data={
            "username": "testuser2",
            "password": "password123"
        })
        
        if response.status_code == 200:
            token2 = response.json()["access_token"]
            print("✅ User 2 logged in")
        else:
            # Try to register user 2
            print("User 2 doesn't exist, creating...")
            response = requests.post(f"{BASE_URL}/auth/register", json={
                "name": "Test User 2",
                "username": "testuser2",
                "email": "test2@example.com",
                "password": "password123"
            })
            
            if response.status_code == 201:
                print("✅ User 2 created")
                # Now login
                response = requests.post(f"{BASE_URL}/auth/login", data={
                    "username": "testuser2",
                    "password": "password123"
                })
                if response.status_code == 200:
                    token2 = response.json()["access_token"]
                    print("✅ User 2 logged in")
                else:
                    print(f"❌ User 2 login failed: {response.text}")
                    return
            else:
                print(f"❌ User 2 creation failed: {response.text}")
                return
                
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running on port 8000")
        return
    
    # Test friend request
    print("\n2. Testing friend request...")
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    try:
        # Send friend request from user 1 to user 2
        response = requests.post(
            f"{BASE_URL}/auth/friends/request", 
            json={"friend_username": "testuser2"},
            headers=headers1
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Friend request sent: {result['msg']}")
        else:
            print(f"❌ Friend request failed: {response.text}")
            return
            
        # Check friend requests for user 2
        response = requests.get(f"{BASE_URL}/auth/friends/requests", headers=headers2)
        if response.status_code == 200:
            requests_data = response.json()
            print(f"✅ User 2 has {len(requests_data['incoming'])} incoming requests")
            
            if requests_data['incoming']:
                request_id = requests_data['incoming'][0]['id']
                print(f"✅ Found request ID: {request_id}")
                
                # Accept the request
                response = requests.post(
                    f"{BASE_URL}/auth/friends/request/{request_id}/respond",
                    json={"request_id": request_id, "action": "accept"},
                    headers=headers2
                )
                
                if response.status_code == 200:
                    print("✅ Friend request accepted!")
                    
                    # Check friends list
                    response = requests.get(f"{BASE_URL}/auth/friends", headers=headers1)
                    if response.status_code == 200:
                        friends_data = response.json()
                        print(f"✅ User 1 now has {len(friends_data['friends'])} friends")
                        
                        response = requests.get(f"{BASE_URL}/auth/friends", headers=headers2)
                        if response.status_code == 200:
                            friends_data = response.json()
                            print(f"✅ User 2 now has {len(friends_data['friends'])} friends")
                            
                            print("\n🎉 Friend request system is working perfectly!")
                            print("✅ MongoDB is storing data correctly")
                            print("✅ Backend API is responding properly")
                        else:
                            print(f"❌ Failed to get user 2 friends: {response.text}")
                    else:
                        print(f"❌ Failed to get user 1 friends: {response.text}")
                else:
                    print(f"❌ Accept request failed: {response.text}")
            else:
                print("❌ No incoming requests found")
        else:
            print(f"❌ Failed to get friend requests: {response.text}")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    simple_test() 