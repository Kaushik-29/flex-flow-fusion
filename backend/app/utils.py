import os
import firebase_admin
from firebase_admin import auth
from dotenv import load_dotenv

load_dotenv()

def decode_access_token(token: str):
    """
    Verifies and decodes the Firebase ID token using the Firebase Admin SDK.
    """
    try:
        # Check if Firebase is initialized
        if not firebase_admin._apps:
            print("WARNING: Firebase Admin is not initialized. Using fallback mock decoding.")
            # Return a mock payload for local testing when credentials are not yet present
            import jwt as pyjwt
            try:
                return pyjwt.decode(token, options={"verify_signature": False})
            except Exception:
                return {
                    "sub": "mock-firebase-uid-123",
                    "email": "testuser@gmail.com",
                    "name": "Mock User",
                    "firebase": {
                        "sign_in_provider": "password"
                    }
                }

        # Verify the ID token securely via Google/Firebase Auth servers
        decoded_token = auth.verify_id_token(token)
        # Map 'uid' to 'sub' to keep compatibility with JWT routers
        if "uid" in decoded_token and "sub" not in decoded_token:
            decoded_token["sub"] = decoded_token["uid"]
        return decoded_token
    except Exception as e:
        print(f"Firebase token verification failed: {e}")
        return None
