from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from .db import get_database
from .auth import get_current_user
from bson import ObjectId

router = APIRouter(tags=["points"])

# Exercise configurations with reps per cycle
EXERCISE_CONFIGS = {
    "squat": {"reps_per_cycle": 15, "points_per_cycle": 15},
    "push-up": {"reps_per_cycle": 10, "points_per_cycle": 10},
    "forward lunge": {"reps_per_cycle": 12, "points_per_cycle": 12},
    "side lunge": {"reps_per_cycle": 12, "points_per_cycle": 12},
    "jumping jack": {"reps_per_cycle": 20, "points_per_cycle": 20},
    "plank": {"reps_per_cycle": 5, "points_per_cycle": 15},  # 5 reps = 3 seconds each
    "mountain climber": {"reps_per_cycle": 15, "points_per_cycle": 15},
    "high knees": {"reps_per_cycle": 20, "points_per_cycle": 20},
    "burpee": {"reps_per_cycle": 8, "points_per_cycle": 16},  # Burpees worth more points
    "jump squat": {"reps_per_cycle": 12, "points_per_cycle": 18}  # Jump squats worth more points
}

class PointsEarned(BaseModel):
    exercise: str
    cycles_completed: int
    points_earned: int
    timestamp: datetime

class UserPoints(BaseModel):
    user_id: str
    total_points: int
    exercise_points: dict
    last_updated: datetime

@router.post("/calculate")
async def calculate_points(
    exercise: str,
    reps_completed: int,
    current_user = Depends(get_current_user)
):
    """Calculate points for a completed workout session"""
    db = get_database()
    points_collection = db["user_points"]
    
    exercise_lower = exercise.lower()
    if exercise_lower not in EXERCISE_CONFIGS:
        raise HTTPException(status_code=400, detail=f"Exercise '{exercise}' not supported")
    
    config = EXERCISE_CONFIGS[exercise_lower]
    reps_per_cycle = config["reps_per_cycle"]
    points_per_cycle = config["points_per_cycle"]
    
    # Calculate completed cycles (no partial points)
    cycles_completed = reps_completed // reps_per_cycle
    points_earned = cycles_completed * points_per_cycle
    
    # Get or create user points record
    user_id = current_user.get("username")
    user_points = points_collection.find_one({"user_id": user_id})
    
    if not user_points:
        user_points = {
            "user_id": user_id,
            "total_points": 0,
            "exercise_points": {},
            "last_updated": datetime.utcnow()
        }
        points_collection.insert_one(user_points)
    
    # Update points
    current_exercise_points = user_points.get("exercise_points", {}).get(exercise_lower, 0)
    new_exercise_points = current_exercise_points + points_earned
    new_total_points = user_points["total_points"] + points_earned
    
    # Update database
    points_collection.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "total_points": new_total_points,
                f"exercise_points.{exercise_lower}": new_exercise_points,
                "last_updated": datetime.utcnow()
            }
        }
    )
    
    # Record the points earned for this session
    session_record = {
        "user_id": user_id,
        "exercise": exercise_lower,
        "reps_completed": reps_completed,
        "cycles_completed": cycles_completed,
        "points_earned": points_earned,
        "timestamp": datetime.utcnow()
    }
    
    db["points_history"].insert_one(session_record)
    
    return {
        "exercise": exercise,
        "reps_completed": reps_completed,
        "cycles_completed": cycles_completed,
        "points_earned": points_earned,
        "reps_per_cycle": reps_per_cycle,
        "total_points": new_total_points,
        "exercise_points": new_exercise_points
    }

@router.get("/user")
async def get_user_points(current_user = Depends(get_current_user)):
    """Get current user's points"""
    db = get_database()
    points_collection = db["user_points"]
    
    user_id = current_user.get("username")
    user_points = points_collection.find_one({"user_id": user_id})
    
    if not user_points:
        return {
            "user_id": user_id,
            "total_points": 0,
            "exercise_points": {},
            "last_updated": datetime.utcnow()
        }
    
    return user_points

@router.get("/leaderboard")
async def get_points_leaderboard(limit: int = 50):
    """Get global points leaderboard"""
    db = get_database()
    points_collection = db["user_points"]
    users_collection = db["users"]
    
    # Get top users by total points
    top_users = list(points_collection.find().sort("total_points", -1).limit(limit))
    
    leaderboard = []
    for i, user_points in enumerate(top_users):
        user = users_collection.find_one({"_id": ObjectId(user_points["user_id"])})
        if user:
            leaderboard.append({
                "rank": i + 1,
                "user_id": user_points["user_id"],
                "name": user.get("name", user.get("username", "Unknown")),
                "username": user.get("username", "Unknown"),
                "total_points": user_points.get("total_points", 0),
                "exercise_points": user_points.get("exercise_points", {}),
                "last_updated": user_points.get("last_updated")
            })
    
    return {"leaderboard": leaderboard}

@router.get("/friends")
async def get_friends_points(current_user = Depends(get_current_user)):
    """Get points for user's friends"""
    db = get_database()
    points_collection = db["user_points"]
    friends_collection = db["friends"]
    
    user_id = current_user.get("username")
    
    # Get user's friends
    friends = list(friends_collection.find({
        "$or": [
            {"user_id": user_id, "status": "accepted"},
            {"friend_id": user_id, "status": "accepted"}
        ]
    }))
    
    friend_ids = []
    for friend in friends:
        if friend["user_id"] == user_id:
            friend_ids.append(friend["friend_id"])
        else:
            friend_ids.append(friend["user_id"])
    
    # Get points for friends
    friends_points = list(points_collection.find({"user_id": {"$in": friend_ids}}))
    
    # Get current user's points
    user_points = points_collection.find_one({"user_id": user_id})
    current_user_points = user_points.get("total_points", 0) if user_points else 0
    
    return {
        "current_user_points": current_user_points,
        "friends_points": friends_points
    }

@router.get("/history")
async def get_points_history(
    exercise: Optional[str] = None,
    limit: int = 20,
    current_user = Depends(get_current_user)
):
    """Get user's points history"""
    db = get_database()
    history_collection = db["points_history"]
    
    user_id = current_user.get("username")
    query = {"user_id": user_id}
    
    if exercise:
        query["exercise"] = exercise.lower()
    
    history = list(history_collection.find(query).sort("timestamp", -1).limit(limit))
    
    # Format the data
    for record in history:
        record["id"] = str(record["_id"])
        del record["_id"]
    
    return {"history": history}

@router.get("/config")
async def get_exercise_configs():
    """Get exercise configurations"""
    return {"exercise_configs": EXERCISE_CONFIGS} 