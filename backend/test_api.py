import requests
import json

BASE_URL = "http://localhost:8000"

def test_backend():
    print("Testing FLEX-IT-OUT Backend API...")
    
    # Test health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test registration
    print("\n2. Testing user registration...")
    try:
        user_data = {
            "name": "Test User",
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test login
    print("\n3. Testing user login...")
    try:
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"Token received: {token[:20]}...")
        else:
            token = None
    except Exception as e:
        print(f"Error: {e}")
        token = None
    
    # Test leaderboard (without auth for now)
    print("\n4. Testing leaderboard...")
    try:
        response = requests.get(f"{BASE_URL}/leaderboard/top?period=alltime&limit=5")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test pose feedback
    print("\n5. Testing pose feedback...")
    try:
        pose_data = {
            "pose_type": "squat",
            "keypoints": [
                {"x": 0.5, "y": 0.3, "score": 0.9},
                {"x": 0.5, "y": 0.6, "score": 0.8},
                {"x": 0.5, "y": 0.8, "score": 0.7}
            ],
            "user_id": "testuser"
        }
        response = requests.post(f"{BASE_URL}/pose-feedback", json=pose_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_backend() 