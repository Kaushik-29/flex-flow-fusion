# FLEX-IT-OUT Backend

A FastAPI backend for the FLEX-IT-OUT fitness app with JWT authentication, MongoDB integration, and AI pose feedback.

## Features

- 🔐 **JWT Authentication** - Secure login/register with token-based auth
- 🏋️‍♂️ **Workout Tracking** - Start, update, and track workout sessions
- 📊 **Leaderboard** - Global and friends rankings with period filtering
- 🧠 **Pose Feedback** - AI-powered pose analysis and feedback
- 👥 **Friend System** - Search and add friends
- 🗄️ **MongoDB Integration** - Scalable NoSQL database

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app entry point
│   ├── db.py            # MongoDB connection utilities
│   ├── models.py        # Pydantic models
│   ├── utils.py         # JWT and password utilities
│   ├── auth.py          # Authentication endpoints
│   ├── workout.py       # Workout session endpoints
│   ├── leaderboard.py   # Leaderboard endpoints
│   └── pose_feedback.py # Pose analysis endpoints
├── requirements.txt
├── test_api.py
└── README.md
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up MongoDB:**
   - Install MongoDB locally or use MongoDB Atlas
   - Set `MONGO_URI` environment variable (default: `mongodb://localhost:27017/`)

3. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Test the API:**
   ```bash
   python test_api.py
   ```

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login with JWT token
- `GET /auth/me` - Get current user profile
- `POST /auth/friends/request` - Send friend request

### Workout (`/workout`)
- `POST /workout/start` - Start workout session
- `POST /workout/update` - Update session with reps/accuracy
- `GET /workout/history` - Get user's workout history

### Leaderboard (`/leaderboard`)
- `GET /leaderboard/top` - Get top users (supports daily/weekly/alltime)
- `GET /leaderboard/search` - Search users by username

### Pose Feedback
- `POST /pose-feedback` - Analyze pose keypoints and return feedback

## Data Models

### User
```json
{
  "id": "string",
  "name": "string",
  "username": "string",
  "email": "string",
  "hashed_password": "string"
}
```

### WorkoutSession
```json
{
  "id": "string",
  "user_id": "string",
  "type": "string",
  "reps": "number",
  "feedback": "string",
  "accuracy": "number",
  "timestamp": "datetime"
}
```

## Frontend Integration

The frontend can now connect to this backend using the API service in `frontend/src/lib/api.ts`. The Leaderboard component has been updated to use real data instead of mock data.

## Environment Variables

- `MONGO_URI` - MongoDB connection string
- `JWT_SECRET` - Secret key for JWT tokens (change in production)

## Testing

Run the test script to verify all endpoints:
```bash
python test_api.py
```

## Next Steps

- Add more pose types (push-ups, planks, etc.)
- Implement real-time notifications
- Add workout challenges
- Implement friend system with requests/acceptance
- Add user avatars and profile pictures 