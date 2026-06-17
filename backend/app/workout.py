from fastapi import APIRouter, Depends, HTTPException
from app.db import workout_repository
from app.auth import get_current_user
from datetime import datetime
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
    session = {
        "user_id": user.get("username"),
        "type": data.type,
        "reps": 0,
        "feedback": "",
        "accuracy": 0.0,
        "timestamp": datetime.utcnow().isoformat()
    }
    result = workout_repository.create(session)
    return {"session_id": str(result.get("id"))}

@router.post("/update")
def update_workout(data: WorkoutUpdateRequest, user=Depends(get_current_user)):
    session = workout_repository.get_by_id(data.session_id)
    if not session or session.get("user_id") != user.get("username"):
        raise HTTPException(status_code=404, detail="Session not found")
    
    workout_repository.update(data.session_id, {
        "reps": data.reps,
        "accuracy": data.accuracy,
        "feedback": data.feedback
    })
    return {"msg": "Workout updated"}

@router.get("/history")
def workout_history(user=Depends(get_current_user)):
    sessions = workout_repository.get_history(user.get("username"))
    for s in sessions:
        s["id"] = str(s.get("id"))
    return {"history": sessions}