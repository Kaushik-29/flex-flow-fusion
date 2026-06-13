from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth import router as auth_router
from app.leaderboard import router as leaderboard_router
from app.workout import router as workout_router
from app.pose_feedback import router as pose_feedback_router
from app.notifications import router as notifications_router
from app.points import router as points_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://flexflowfusion.netlify.app",
        "http://localhost:8080",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"https://([a-z0-9-]+\.)?netlify\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(leaderboard_router, tags=["leaderboard"])
app.include_router(workout_router, tags=["workout"])
app.include_router(pose_feedback_router)
app.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
app.include_router(points_router, prefix="/points", tags=["points"])

@app.get("/")
def root():
    return {
        "message": "FLEX-IT-OUT FastAPI backend is running!"
    }
