import requests
import json

# Test the notifications endpoint
def test_notifications():
    try:
        # First, let's try to get notifications without auth to see if the server is running
        response = requests.get("http://localhost:8000/notifications/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 401:
            print("✅ Server is running - got expected 401 (unauthorized)")
            print("The validation error should be fixed now!")
        else:
            print(f"Unexpected response: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the backend server first.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_notifications() 