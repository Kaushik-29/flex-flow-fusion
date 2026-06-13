from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models import UserCreate, UserLogin, User, UserInDB
from app.db import get_user_collection, get_database
from app.utils import hash_password, verify_password, create_access_token, decode_access_token
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class FriendRequest(BaseModel):
    friend_username: str

class FriendRequestResponse(BaseModel):
    request_id: str
    action: str  # "accept" or "reject"

@router.post("/register", status_code=201)
def register(user: UserCreate):
    users = get_user_collection()
    if users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed = hash_password(user.password)
    user_dict = {
        "name": user.name,
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed,
        "created_at": datetime.utcnow()
    }
    users.insert_one(user_dict)
    return {"msg": "User registered successfully"}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users = get_user_collection()
    user = users.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user["_id"])})
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = payload.get("sub")
    users = get_user_collection()
    user = users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return a simple dict instead of UserInDB model to avoid conversion issues
    return {
        "id": str(user["_id"]),
        "name": user.get("name"),
        "username": user.get("username"),
        "email": user.get("email"),
        "hashed_password": user.get("hashed_password")
    }

@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return {
        "name": user.get("name"),
        "username": user.get("username"),
        "email": user.get("email"),
    }

@router.post("/friends/request")
def send_friend_request(request: FriendRequest, current_user=Depends(get_current_user)):
    db = get_database()
    users = db["users"]
    friend_requests = db["friend_requests"]
    
    # Check if friend exists
    friend = users.find_one({"username": request.friend_username})
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent self-friend request
    if current_user.get("username") == request.friend_username:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")
    
    # Check if request already exists
    existing_request = friend_requests.find_one({
        "from_username": current_user.get("username"),
        "to_username": request.friend_username,
        "status": "pending"
    })
    
    if existing_request:
        raise HTTPException(status_code=400, detail="Friend request already sent")
    
    # Check if they are already friends
    existing_request_reverse = friend_requests.find_one({
        "from_username": request.friend_username,
        "to_username": current_user.get("username"),
        "status": "pending"
    })
    
    if existing_request_reverse:
        raise HTTPException(status_code=400, detail="This user has already sent you a friend request")
    
    # Create friend request
    friend_request = {
        "from_username": current_user.get("username"),
        "to_username": request.friend_username,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    result = friend_requests.insert_one(friend_request)
    
    return {
        "msg": f"Friend request sent to {request.friend_username}",
        "request_id": str(result.inserted_id)
    }

@router.get("/friends/requests")
def get_friend_requests(current_user=Depends(get_current_user)):
    db = get_database()
    friend_requests = db["friend_requests"]
    
    # Get incoming friend requests
    incoming_requests = list(friend_requests.find({
        "to_username": current_user.get("username"),
        "status": "pending"
    }))
    
    # Get outgoing friend requests
    outgoing_requests = list(friend_requests.find({
        "from_username": current_user.get("username"),
        "status": "pending"
    }))
    
    # Format the data
    def format_request(req):
        req["id"] = str(req["_id"])
        del req["_id"]
        return req
    
    return {
        "incoming": [format_request(req) for req in incoming_requests],
        "outgoing": [format_request(req) for req in outgoing_requests]
    }

@router.post("/friends/request/{request_id}/respond")
def respond_to_friend_request(
    request_id: str, 
    response: FriendRequestResponse, 
    current_user=Depends(get_current_user)
):
    db = get_database()
    friend_requests = db["friend_requests"]
    
    # Find the request
    request_obj = friend_requests.find_one({
        "_id": ObjectId(request_id),
        "to_username": current_user.get("username"),
        "status": "pending"
    })
    
    if not request_obj:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    if response.action not in ["accept", "reject"]:
        raise HTTPException(status_code=400, detail="Action must be 'accept' or 'reject'")
    
    # Update the request status
    friend_requests.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {"status": response.action, "responded_at": datetime.utcnow()}}
    )
    
    if response.action == "accept":
        # Add to friends collection (optional - for tracking friendships)
        friends = db["friends"]
        friendship = {
            "user1": current_user.get("username"),
            "user2": request_obj["from_username"],
            "created_at": datetime.utcnow()
        }
        friends.insert_one(friendship)
    
    return {
        "msg": f"Friend request {response.action}ed",
        "action": response.action
    }

@router.get("/friends")
def get_friends(current_user=Depends(get_current_user)):
    db = get_database()
    friends = db["friends"]
    
    # Get all friendships for this user
    user_friendships = list(friends.find({
        "$or": [
            {"user1": current_user.get("username")},
            {"user2": current_user.get("username")}
        ]
    }))
    
    # Extract friend usernames
    friend_usernames = []
    for friendship in user_friendships:
        if friendship["user1"] == current_user.get("username"):
            friend_usernames.append(friendship["user2"])
        else:
            friend_usernames.append(friendship["user1"])
    
    # Get friend details
    users = db["users"]
    friend_details = []
    for username in friend_usernames:
        user = users.find_one({"username": username})
        if user:
            friend_details.append({
                "username": user["username"],
                "name": user.get("name", ""),
                "email": user["email"]
            })
    
    return {"friends": friend_details} 