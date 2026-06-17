from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models import UserCreate, UserLogin
from app.db import user_repository, friend_repository
from app.utils import decode_access_token
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import os
import requests

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class FriendRequest(BaseModel):
    friend_username: str

class FriendRequestResponse(BaseModel):
    request_id: str
    action: str  # "accept" or "reject"


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token structure")
        
    user = user_repository.get_by_id(user_id)
    if not user:
        # Fallback profile creation if the trigger has not yet completed
        user_metadata = payload.get("user_metadata", {})
        email = payload.get("email") or ""
        username = payload.get("username") or user_metadata.get("username") or email.split("@")[0]
        name = payload.get("name") or user_metadata.get("name") or user_metadata.get("full_name") or username
        avatar = payload.get("picture") or user_metadata.get("avatar_url") or ""
        
        user = user_repository.create({
            "id": user_id,
            "username": username,
            "email": email,
            "name": name,
            "avatar": avatar,
            "created_at": datetime.utcnow().isoformat()
        })
        
    return {
        "id": str(user.get("id")),
        "name": user.get("name"),
        "username": user.get("username"),
        "email": user.get("email")
    }


@router.post("/register", status_code=201)
def register(user: UserCreate):
    try:
        # Check if username or email already exists in our profiles
        if user_repository.get_by_username(user.username):
            raise HTTPException(status_code=400, detail="Username already exists")
        if user_repository.get_by_email(user.email):
            raise HTTPException(status_code=400, detail="Email already exists")
        
        user_id = None
        import firebase_admin
        # Call Firebase signup if initialized
        if firebase_admin._apps:
            try:
                from firebase_admin import auth as firebase_auth
                user_record = firebase_auth.create_user(
                    email=user.email,
                    password=user.password,
                    display_name=user.name
                )
                user_id = user_record.uid
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        else:
            # Fallback mock user ID
            user_id = f"mock-uid-{user.username}"
        
        # Create user profile manually in our local/Firestore DB
        user_repository.create({
            "id": user_id,
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "avatar": "",
            "created_at": datetime.utcnow().isoformat()
        })
            
        return {"msg": "User registered successfully"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        username_or_email = form_data.username
        email = username_or_email
        password = form_data.password
        
        # If the username is not an email, resolve it to an email using user_repository
        profile = None
        if "@" not in username_or_email:
            profile = user_repository.get_by_username(username_or_email)
            if not profile:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            email = profile.get("email")
        else:
            profile = user_repository.get_by_email(username_or_email)
            
        import firebase_admin
        api_key = os.getenv("FIREBASE_API_KEY")
        if firebase_admin._apps and api_key:
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            r = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}",
                json=payload
            )
            if r.status_code == 200:
                res_data = r.json()
                return {"access_token": res_data["idToken"], "token_type": "bearer"}
            else:
                try:
                    err_msg = r.json().get("error", {}).get("message", "Invalid credentials")
                except Exception:
                    err_msg = "Invalid credentials"
                raise HTTPException(status_code=401, detail=err_msg)
        else:
            # Fallback / mock mode
            if not profile:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            import jwt as pyjwt
            mock_payload = {
                "sub": profile["id"],
                "email": profile["email"],
                "name": profile.get("name", ""),
                "username": profile.get("username", ""),
                "exp": datetime.utcnow().timestamp() + 86400
            }
            token = pyjwt.encode(mock_payload, "mock_secret", algorithm="HS256")
            return {"access_token": token, "token_type": "bearer"}
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return {
        "name": user.get("name"),
        "username": user.get("username"),
        "email": user.get("email"),
    }


@router.get("/resolve-email")
def resolve_email(username: str):
    profile = user_repository.get_by_username(username)
    if not profile:
        raise HTTPException(status_code=404, detail="Username not found")
    return {"email": profile.get("email")}



@router.post("/friends/request")
def send_friend_request(request: FriendRequest, current_user=Depends(get_current_user)):
    username = current_user.get("username")
    
    # Check if friend exists
    friend = user_repository.get_by_username(request.friend_username)
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-friend request
    if username == request.friend_username:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")
    
    # Check if request already exists
    existing_requests = friend_repository.get_requests_for_user(username)
    for r in existing_requests:
        if r["from_username"] == username and r["to_username"] == request.friend_username:
            raise HTTPException(status_code=400, detail="Friend request already sent")
        if r["from_username"] == request.friend_username and r["to_username"] == username:
            raise HTTPException(status_code=400, detail="This user has already sent you a friend request")
    
    # Create friend request
    friend_request = {
        "from_username": username,
        "to_username": request.friend_username,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    
    result = friend_repository.send_request(friend_request)
    
    return {
        "msg": f"Friend request sent to {request.friend_username}",
        "request_id": str(result.get("id"))
    }


@router.get("/friends/requests")
def get_friend_requests(current_user=Depends(get_current_user)):
    username = current_user.get("username")
    requests_list = friend_repository.get_requests_for_user(username)
    
    incoming = []
    outgoing = []
    
    for r in requests_list:
        formatted = {
            "id": str(r["id"]),
            "from_username": r["from_username"],
            "to_username": r["to_username"],
            "status": r["status"],
            "created_at": r["created_at"]
        }
        if r["to_username"] == username:
            incoming.append(formatted)
        else:
            outgoing.append(formatted)
    
    return {
        "incoming": incoming,
        "outgoing": outgoing
    }


@router.post("/friends/request/{request_id}/respond")
def respond_to_friend_request(
    request_id: str, 
    response: FriendRequestResponse, 
    current_user=Depends(get_current_user)
):
    username = current_user.get("username")
    
    # Find the request
    request_obj = friend_repository.get_request(request_id, username)
    if not request_obj:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    if response.action not in ["accept", "reject"]:
        raise HTTPException(status_code=400, detail="Action must be 'accept' or 'reject'")
    
    # Update the request status
    success = friend_repository.respond_to_request(request_id, response.action)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to respond to request")
    
    if response.action == "accept":
        # Add to friends collection
        friendship = {
            "user1": username,
            "user2": request_obj["from_username"],
            "status": "accepted",
            "created_at": datetime.utcnow().isoformat()
        }
        friend_repository.create_friendship(friendship)
    
    return {
        "msg": f"Friend request {response.action}ed",
        "action": response.action
    }


@router.get("/friends")
def get_friends(current_user=Depends(get_current_user)):
    username = current_user.get("username")
    friendships = friend_repository.get_friends(username)
    
    # Extract friend usernames
    friend_usernames = []
    for friendship in friendships:
        if friendship["user1"] == username:
            friend_usernames.append(friendship["user2"])
        else:
            friend_usernames.append(friendship["user1"])
    
    # Get friend details
    friend_details = []
    for f_username in friend_usernames:
        friend_user = user_repository.get_by_username(f_username)
        if friend_user:
            friend_details.append({
                "username": friend_user["username"],
                "name": friend_user.get("name", ""),
                "email": friend_user["email"]
            })
    
    return {"friends": friend_details}