import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth():
    print("Testing authentication endpoints...")
    
    # Test registration
    print("\n1. Testing registration...")
    register_data = {
        "name": "Test User 2",
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Registration response: {response.status_code}")
        if response.status_code == 201:
            print("✅ Registration successful")
        else:
            print(f"❌ Registration failed: {response.text}")
    except Exception as e:
        print(f"❌ Registration error: {e}")
    
    # Test login
    print("\n2. Testing login...")
    login_data = {
        "username": "testuser2",
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"Login response: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print("✅ Login successful")
            print(f"Token: {token[:20]}...")
            
            # Test /me endpoint
            print("\n3. Testing /me endpoint...")
            headers = {"Authorization": f"Bearer {token}"}
            me_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            print(f"/me response: {me_response.status_code}")
            if me_response.status_code == 200:
                user_data = me_response.json()
                print("✅ /me successful")
                print(f"User data: {user_data}")
            else:
                print(f"❌ /me failed: {me_response.text}")
                
            # Test friend request
            print("\n4. Testing friend request...")
            friend_data = {"friend_username": "anotheruser"}
            friend_response = requests.post(f"{BASE_URL}/auth/friends/request", json=friend_data, headers=headers)
            print(f"Friend request response: {friend_response.status_code}")
            if friend_response.status_code == 200:
                print("✅ Friend request successful")
            else:
                print(f"❌ Friend request failed: {friend_response.text}")
                
        else:
            print(f"❌ Login failed: {response.text}")
    except Exception as e:
        print(f"❌ Login error: {e}")

if __name__ == "__main__":
    test_auth() 