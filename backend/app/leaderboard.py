from fastapi import APIRouter, Query
from app.db import get_user_collection, get_workout_collection
from datetime import datetime, timedelta
from typing import Optional, Any

router = APIRouter(prefix="/leaderboard")

def get_badge_by_rank(rank: int) -> str:
    if rank == 1:
        return "🏆"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    elif rank <= 10:
        return "⚡"
    elif rank <= 50:
        return "💪"
    else:
        return "🔥"

@router.get("/top")
def get_leaderboard(
    period: str = Query("alltime", description="Period: daily, weekly, alltime"),
    limit: int = Query(10, description="Number of top users to return")
):
    workouts = get_workout_collection()
    users = get_user_collection()
    
    # Calculate date filter based on period
    now = datetime.utcnow()
    if period == "daily":
        start_date = now - timedelta(days=1)
    elif period == "weekly":
        start_date = now - timedelta(weeks=1)
    else:  # alltime
        start_date = None
    
    # Build aggregation pipeline
    pipeline: list[dict[str, Any]] = [
        {"$group": {
            "_id": "$user_id",
            "total_reps": {"$sum": "$reps"},
            "avg_accuracy": {"$avg": "$accuracy"},
            "total_workouts": {"$sum": 1}
        }}
    ]
    
    # Add date filter if needed
    if start_date:
        pipeline.insert(0, {"$match": {"timestamp": {"$gte": start_date}}})
    
    # Add sorting and limiting
    pipeline.extend([
        {"$sort": {"total_reps": -1}},
        {"$limit": limit}
    ])
    
    results = list(workouts.aggregate(pipeline))
    leaderboard = []
    
    for i, entry in enumerate(results):
        user = users.find_one({"_id": entry["_id"]})
        if user:
            rank = i + 1
            leaderboard.append({
                "rank": rank,
                "user_id": str(entry["_id"]),
                "name": user.get("name", user.get("username", "Unknown")),
                "username": user.get("username", "Unknown"),
                "avatar": user.get("avatar", ""),
                "points": entry["total_reps"],
                "badge": get_badge_by_rank(rank),
                "avg_accuracy": round(entry["avg_accuracy"], 2),
                "total_workouts": entry["total_workouts"],
                "isYou": False  # This will be set by frontend based on current user
            })
    
    return {"leaderboard": leaderboard, "period": period}

@router.get("/search")
def search_users(query: str = Query(..., description="Search query for usernames")):
    users = get_user_collection()
    # Case-insensitive search for username or name
    search_filter = {
        "$or": [
            {"username": {"$regex": query, "$options": "i"}},
            {"name": {"$regex": query, "$options": "i"}}
        ]
    }
    
    results = list(users.find(search_filter).limit(10))
    search_results = []
    
    for user in results:
        search_results.append({
            "user_id": str(user["_id"]),
            "name": user.get("name", user.get("username", "Unknown")),
            "username": user.get("username", "Unknown"),
            "avatar": user.get("avatar", ""),
            "badge": "🔥"  # Default badge for search results
        })
    
    return {"users": search_results} 