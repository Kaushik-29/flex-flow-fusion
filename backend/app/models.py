from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
from pymongo import MongoClient

class Keypoint(BaseModel):
    x: float
    y: float
    score: float

class PoseFeedbackRequest(BaseModel):
    pose_type: str
    keypoints: List[Keypoint]
    user_id: str

class PoseFeedbackResponse(BaseModel):
    tips: List[str]
    score: float

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: Optional[str] = None
    username: str
    email: EmailStr
    hashed_password: str

class UserInDB(User):
    pass

class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class WorkoutSession(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    type: str
    reps: int
    feedback: str
    accuracy: float
    timestamp: datetime

class Session(BaseModel):
    user_id: str
    timestamp: datetime
    feedback: str
    keypoints: list

def get_db():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["pose_app"]
    return db 