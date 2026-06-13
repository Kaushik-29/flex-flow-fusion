from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import router as auth_router
from app.workout import router as workout_router
from app.leaderboard import router as leaderboard_router
from app.pose_feedback import router as pose_feedback_router
from app.notifications import router as notifications_router
from app.points import router as points_router

app = FastAPI(title="FLEX-IT-OUT API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://flexflowfusion.netlify.app", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(workout_router, tags=["Workout"])
app.include_router(leaderboard_router, tags=["Leaderboard"])
app.include_router(pose_feedback_router, tags=["Pose Feedback"])
app.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
app.include_router(points_router, prefix="/points", tags=["Points"])

@app.get("/")
def root():
    return {"message": "FLEX-IT-OUT FastAPI backend is running!"} 