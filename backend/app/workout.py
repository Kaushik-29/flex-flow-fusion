from fastapi import APIRouter, Depends, HTTPException
from app.models import WorkoutSession
from app.db import get_workout_collection
from app.auth import get_current_user
from datetime import datetime
from bson.objectid import ObjectId
from pydantic import BaseModel

router = APIRouter(prefix="/workout")

class WorkoutStartRequest(BaseModel):
    type: str

class WorkoutUpdateRequest(BaseModel):
    session_id: str
    reps: int
    accuracy: float
    feedback: str

@router.post("/start")
def start_workout(data: WorkoutStartRequest, user=Depends(get_current_user)):
    workouts = get_workout_collection()
    session = {
        "user_id": user.get("username"),
        "type": data.type,
        "reps": 0,
        "feedback": "",
        "accuracy": 0.0,
        "timestamp": datetime.utcnow()
    }
    result = workouts.insert_one(session)
    return {"session_id": str(result.inserted_id)}

@router.post("/update")
def update_workout(data: WorkoutUpdateRequest, user=Depends(get_current_user)):
    workouts = get_workout_collection()
    session = workouts.find_one({"_id": ObjectId(data.session_id), "user_id": user.get("username")})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    workouts.update_one(
        {"_id": ObjectId(data.session_id)}, 
        {"$set": {"reps": data.reps, "accuracy": data.accuracy, "feedback": data.feedback}}
    )
    return {"msg": "Workout updated"}

@router.get("/history")
def workout_history(user=Depends(get_current_user)):
    workouts = get_workout_collection()
    sessions = list(workouts.find({"user_id": user.get("username")}))
    for s in sessions:
        s["id"] = str(s["_id"])
        del s["_id"]
    return {"history": sessions} 