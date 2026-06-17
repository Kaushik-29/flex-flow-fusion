# FLEX-IT-OUT 🏋️‍♂️💪

FLEX-IT-OUT is a premium, state-of-the-art, AI-powered fitness companion that helps users track their workouts, receive real-time posture analysis, earn points, and compete with friends. 

The application utilizes **browser-based computer vision** for real-time posture evaluation and features a fully refactored, robust, and highly scalable server architecture backed by **Google Firebase**.

---

## 🏗️ Architecture Overview

```mermaid
graph TD
    subgraph Client Layer (Netlify)
        A[React + TS Frontend] -->|Firebase JS SDK| B[Firebase Auth]
        A -->|Computer Vision| C[TensorFlow.js Pose Detection]
    end
    
    subgraph Server Layer (Render)
        D[FastAPI Backend] -->|Firebase Admin SDK| E[Cloud Firestore]
        A -->|Firebase ID Token| D
    end
```

### 1. Database & Session Management
All persistent storage—including users, workouts, friend requests, notifications, points, and gamification metrics—is hosted on **Cloud Firestore**. 
* **Offline Fallback**: To support seamless local development and offline testing, the database repositories implement an in-memory dictionary-backed fallback (`_OFFLINE_DB`). If Firebase service keys are not present, the backend automatically operates offline, allowing full functionality.

### 2. Unified Authentication
* Handled natively by **Firebase Authentication** supporting both email/password credentials and single-click **Google Sign-In**.
* Backend endpoints are secured using a custom FastAPI dependency that decodes and validates Firebase ID tokens via the Firebase Admin SDK.

---

## ✨ Features

* **Real-time Posture Analysis**: Computer vision evaluates key exercises (squats, pushups, lunges, jacks, planks, climbers, burpees) and provides instant audio-visual guidance.
* **Gamification & Points**: Earn points dynamically based on workout completion. Repetition cycles are calculated automatically.
* **Social Network**: Add friends, track friend requests, and compare daily/weekly scores on the leaderboard.
* **Global Leaderboard**: Standings based on total accumulated points.
* **Real-time Notifications**: Alert systems for friend activities, achievements, and workout reminders.

---

## 🛠️ Technology Stack

* **Frontend**: React, TypeScript, Vite, TailwindCSS, Radix UI (Shadcn), Lucide React.
* **Backend**: Python 3.11+, FastAPI, Uvicorn, PyJWT (for offline testing).
* **Database & Auth**: Google Firebase (Firestore Database, Firebase Auth, Google OAuth).
* **AI Model**: TensorFlow.js Pose-Detection (MoveNet/Blazepose).

---

## 📁 Repository Structure

```
├── backend/
│   ├── app/
│   │   ├── auth.py              # User authentication & friendship routes
│   │   ├── db.py                # Firebase Admin connection & repository layers
│   │   ├── main.py              # Backend router mounting & server config
│   │   ├── models.py            # Pydantic schemas
│   │   ├── points.py            # Point calculations & gamification
│   │   └── workout.py           # Workout sessions & history
│   ├── main.py                  # ASGI Render entrypoint
│   ├── requirements.txt         # Server dependencies
│   └── test_user_data.py        # Integration test scripts
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── auth/            # AuthTabs.tsx (Firebase client logins)
    │   │   ├── dashboard/       # Workout dashboard
    │   │   ├── settings/        # Settings.tsx (User profile & sign-out)
    │   │   └── workout/         # Pose detection webcam interface
    │   ├── lib/
    │   │   ├── api.ts           # Dynamic API token propagation
    │   │   └── firebaseClient.ts# Firebase web client initialization
    │   └── App.tsx
    ├── package.json             # Web dependencies
    └── vite.config.ts           # Bundler settings
```

---

## 🚀 Local Installation & Setup

### Prerequisites
* Python 3.11+
* Node.js 18+

### 1. Setup Backend
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # On Windows
   source venv/bin/activate    # On macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the `backend/` directory:
   ```env
   JWT_SECRET=your-local-jwt-secret-key
   FIREBASE_SERVICE_ACCOUNT_KEY=firebase-key.json
   FIREBASE_API_KEY=your_firebase_web_api_key
   ```
5. *(Optional)* Download your Firebase Private Key JSON from Project Settings > Service Accounts and save it as `backend/firebase-key.json`. If skipped, the server automatically starts in offline fallback mode.

### 2. Setup Frontend
1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Create a `.env` file in the `frontend/` directory:
   ```env
   VITE_FIREBASE_API_KEY=your_firebase_web_api_key
   VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   VITE_FIREBASE_PROJECT_ID=your_project_id
   VITE_FIREBASE_STORAGE_BUCKET=your_project.firebasestorage.app
   VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   VITE_FIREBASE_APP_ID=your_app_id
   VITE_API_URL=http://localhost:8000
   ```

---

## 🏃 Running the Application Locally

1. **Start Backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
   The backend will be running at [http://localhost:8000](http://localhost:8000).

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```
   The web portal will be accessible at [http://localhost:8080](http://localhost:8080).

3. **Verify API Integrity**:
   Run the test suite to ensure endpoints, authentication fallbacks, and database connections work correctly:
   ```bash
   cd backend
   python test_user_data.py
   python test_all_endpoints.py
   ```

---

## 🌐 Production Deployment Configurations

### 1. Backend (Render Deployment)
* **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
* **Environment Variables**:
  * `FIREBASE_API_KEY`: Your Firebase Web API Key.
  * `FIREBASE_SERVICE_ACCOUNT_JSON`: Copy and paste the entire text contents of your `firebase-key.json` file as a single string. (Our system will parse this JSON string dynamically at startup).

### 2. Frontend (Netlify Deployment)
* **Build Command**: `npm run build`
* **Publish Directory**: `dist`
* **Environment Variables**: Make sure to add the keys (starting with `VITE_`) from your frontend `.env` to Netlify **Site Settings > Environment Variables**, choosing **Same value for all deploy contexts**, and then trigger a redeploy.
* **Authorized Domain**: Add your `xxxx.netlify.app` domain inside your **Firebase Console > Authentication > Settings > Authorized Domains** so Google Sign-In popups are allowed.
