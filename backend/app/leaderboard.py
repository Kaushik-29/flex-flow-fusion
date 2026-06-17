from fastapi import APIRouter, Query
from app.db import user_repository, workout_repository
from typing import Optional

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
    results = workout_repository.get_leaderboard(period, limit)
    leaderboard = []
    
    for i, entry in enumerate(results):
        # entry["_id"] is the user_id (username) from workouts table
        user = user_repository.get_by_username(entry["_id"])
        if user:
            rank = i + 1
            leaderboard.append({
                "rank": rank,
                "user_id": str(user["id"]),
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
    results = user_repository.search(query)
    search_results = []
    
    for user in results:
        search_results.append({
            "user_id": str(user["id"]),
            "name": user.get("name", user.get("username", "Unknown")),
            "username": user.get("username", "Unknown"),
            "avatar": user.get("avatar", ""),
            "badge": "🔥"  # Default badge for search results
        })
    
    return {"users": search_results}