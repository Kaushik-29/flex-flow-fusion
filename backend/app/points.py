from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.db import points_repository, friend_repository, user_repository
from app.auth import get_current_user

router = APIRouter(tags=["points"])

EXERCISE_CONFIGS = {
    "squat": {"reps_per_cycle": 15, "points_per_cycle": 15},
    "push-up": {"reps_per_cycle": 10, "points_per_cycle": 10},
    "forward lunge": {"reps_per_cycle": 12, "points_per_cycle": 12},
    "side lunge": {"reps_per_cycle": 12, "points_per_cycle": 12},
    "jumping jack": {"reps_per_cycle": 20, "points_per_cycle": 20},
    "plank": {"reps_per_cycle": 5, "points_per_cycle": 15},
    "mountain climber": {"reps_per_cycle": 15, "points_per_cycle": 15},
    "high knees": {"reps_per_cycle": 20, "points_per_cycle": 20},
    "burpee": {"reps_per_cycle": 8, "points_per_cycle": 16},
    "jump squat": {"reps_per_cycle": 12, "points_per_cycle": 18}
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
    exercise_lower = exercise.lower()
    if exercise_lower not in EXERCISE_CONFIGS:
        if exercise_lower.endswith('s') and exercise_lower[:-1] in EXERCISE_CONFIGS:
            exercise_lower = exercise_lower[:-1]
        else:
            raise HTTPException(status_code=400, detail=f"Exercise '{exercise}' not supported")
    
    config = EXERCISE_CONFIGS[exercise_lower]
    reps_per_cycle = config["reps_per_cycle"]
    points_per_cycle = config["points_per_cycle"]
    
    cycles_completed = reps_completed // reps_per_cycle
    points_earned = cycles_completed * points_per_cycle
    
    user_id = current_user.get("username")
    user_points = points_repository.get_by_user(user_id)
    
    if not user_points:
        user_points = {
            "user_id": user_id,
            "total_points": 0,
            "exercise_points": {},
            "last_updated": datetime.utcnow().isoformat()
        }
        points_repository.create(user_points)
    
    current_exercise_points = user_points.get("exercise_points", {}).get(exercise_lower, 0)
    new_exercise_points = current_exercise_points + points_earned
    new_total_points = user_points["total_points"] + points_earned
    
    # Update dict copy to save
    exercise_points_updated = dict(user_points.get("exercise_points", {}))
    exercise_points_updated[exercise_lower] = new_exercise_points
    
    points_repository.update_points(user_id, new_total_points, exercise_points_updated)
    
    session_record = {
        "user_id": user_id,
        "exercise": exercise_lower,
        "reps_completed": reps_completed,
        "cycles_completed": cycles_completed,
        "points_earned": points_earned,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    points_repository.create_history_record(session_record)
    
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
    user_id = current_user.get("username")
    user_points = points_repository.get_by_user(user_id)
    
    if not user_points:
        return {
            "user_id": user_id,
            "total_points": 0,
            "exercise_points": {},
            "last_updated": datetime.utcnow().isoformat()
        }
    
    user_points["id"] = str(user_points.get("id"))
    return user_points

@router.get("/leaderboard")
async def get_points_leaderboard(limit: int = 50):
    """Get global points leaderboard"""
    top_users = points_repository.get_leaderboard(limit)
    leaderboard = []
    
    for i, user_points in enumerate(top_users):
        user = user_repository.get_by_username(user_points["user_id"])
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
    user_id = current_user.get("username")
    
    # Get user's friends (using standardized user1/user2 schema)
    friendships = friend_repository.get_friends(user_id)
    
    friend_ids = []
    for friend in friendships:
        if friend["user1"] == user_id:
            friend_ids.append(friend["user2"])
        else:
            friend_ids.append(friend["user1"])
    
    friends_points = points_repository.get_friends_points(friend_ids)
    
    for fp in friends_points:
        fp["id"] = str(fp.get("id"))
        
    user_points = points_repository.get_by_user(user_id)
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
    user_id = current_user.get("username")
    history = points_repository.get_history(user_id, exercise, limit)
    
    for record in history:
        record["id"] = str(record.get("id"))
    
    return {"history": history}

@router.get("/config")
async def get_exercise_configs():
    """Get exercise configurations"""
    return {"exercise_configs": EXERCISE_CONFIGS}