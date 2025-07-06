import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["flexitout"]

def get_database():
    return db

def get_user_collection():
    return db["users"]

def get_workout_collection():
    return db["workouts"]

def get_scores_collection():
    return db["user_scores"] 