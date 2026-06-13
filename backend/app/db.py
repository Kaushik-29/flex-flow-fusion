import os
from pymongo import MongoClient
<<<<<<< HEAD
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed — rely on system environment variables

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://29skkr2005:rP6QxyV_U5.fW5Q@cluster0.9dofqem.mongodb.net/flexitout?retryWrites=true&w=majority&appName=Cluster0"
)

# Create MongoDB Atlas client
client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)

# Verify connection on startup
try:
    client.admin.command("ping")
    print("[OK] Connected to MongoDB Atlas successfully!")
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    print(f"[ERROR] MongoDB Atlas connection FAILED: {e}")
    raise

=======

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
>>>>>>> 73104143b6642647d1cbb806129d6444f6ec9d2f
db = client["flexitout"]

def get_database():
    return db

def get_user_collection():
    return db["users"]

def get_workout_collection():
    return db["workouts"]

def get_scores_collection():
<<<<<<< HEAD
    return db["user_scores"]
=======
    return db["user_scores"] 
>>>>>>> 73104143b6642647d1cbb806129d6444f6ec9d2f
