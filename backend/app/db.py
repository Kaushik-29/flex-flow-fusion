import os
from datetime import datetime
from typing import Any, List, Optional
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

import json

# Centralized configuration management
KEY_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY") or "firebase-key.json"
firebase_json_str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

db = None
if firebase_json_str:
    try:
        service_account_info = json.loads(firebase_json_str)
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Successfully initialized Firebase Admin SDK from environment JSON string.")
    except Exception as e:
        print(f"Failed to initialize Firebase Admin SDK from environment JSON: {e}")
elif os.path.exists(KEY_PATH):
    try:
        cred = credentials.Certificate(KEY_PATH)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print(f"Successfully initialized Firebase Admin SDK from {KEY_PATH}")
    except Exception as e:
        print(f"Failed to initialize Firebase Admin SDK: {e}")
else:
    print(f"Firebase Service Account Key not found at: {KEY_PATH}. Firestore operations will fail until configured.")


# ----------------- OFFLINE MOCK DATABASE -----------------
_OFFLINE_DB = {
    "users": {},
    "workouts": {},
    "friend_requests": {},
    "friends": [],
    "notifications": {},
    "user_points": {},
    "points_history": [],
    "sessions": {}
}

# ----------------- REPOSITORY LAYER -----------------

class UserRepository:
    def get_by_id(self, user_id: str) -> Optional[dict]:
        if not db:
            return _OFFLINE_DB["users"].get(user_id)
        try:
            doc = db.collection("users").document(user_id).get()
            return {"id": doc.id, **doc.to_dict()} if doc.exists else None
        except Exception as e:
            print(f"UserRepository.get_by_id error: {e}")
            return None

    def get_by_username(self, username: str) -> Optional[dict]:
        if not db:
            for u in _OFFLINE_DB["users"].values():
                if u.get("username") == username:
                    return u
            return None
        try:
            docs = db.collection("users").where("username", "==", username).limit(1).get()
            return {"id": docs[0].id, **docs[0].to_dict()} if docs else None
        except Exception as e:
            print(f"UserRepository.get_by_username error: {e}")
            return None

    def get_by_email(self, email: str) -> Optional[dict]:
        if not db:
            for u in _OFFLINE_DB["users"].values():
                if u.get("email") == email:
                    return u
            return None
        try:
            docs = db.collection("users").where("email", "==", email).limit(1).get()
            return {"id": docs[0].id, **docs[0].to_dict()} if docs else None
        except Exception as e:
            print(f"UserRepository.get_by_email error: {e}")
            return None

    def create(self, user_data: dict) -> dict:
        if not db:
            uid = user_data.get("id")
            _OFFLINE_DB["users"][uid] = user_data
            return user_data
        try:
            uid = user_data.get("id")
            data = dict(user_data)
            data.pop("id", None)
            db.collection("users").document(uid).set(data)
            return user_data
        except Exception as e:
            print(f"UserRepository.create error: {e}")
            return user_data

    def search(self, query: str) -> List[dict]:
        if not db:
            results = []
            q = query.lower()
            for u in _OFFLINE_DB["users"].values():
                username = u.get("username", "").lower()
                name = u.get("name", "").lower()
                if q in username or q in name:
                    results.append(u)
            return results[:10]
        try:
            # Fetch and filter in-memory to bypass complex Firestore indexing
            docs = db.collection("users").stream()
            results = []
            q = query.lower()
            for doc in docs:
                d = doc.to_dict()
                username = d.get("username", "").lower()
                name = d.get("name", "").lower()
                if q in username or q in name:
                    results.append({"id": doc.id, **d})
                    if len(results) >= 10:
                        break
            return results
        except Exception as e:
            print(f"UserRepository.search error: {e}")
            return []


class WorkoutRepository:
    def create(self, workout_data: dict) -> dict:
        if not db:
            import uuid
            data = dict(workout_data)
            data["id"] = data.get("id") or str(uuid.uuid4())
            _OFFLINE_DB["workouts"][data["id"]] = data
            return data
        try:
            doc_ref = db.collection("workouts").document()
            data = dict(workout_data)
            data["id"] = doc_ref.id
            doc_ref.set(data)
            return data
        except Exception as e:
            print(f"WorkoutRepository.create error: {e}")
            raise e

    def update(self, session_id: str, update_data: dict) -> bool:
        if not db:
            if session_id in _OFFLINE_DB["workouts"]:
                _OFFLINE_DB["workouts"][session_id].update(update_data)
                return True
            return False
        try:
            db.collection("workouts").document(session_id).update(update_data)
            return True
        except Exception as e:
            print(f"WorkoutRepository.update error: {e}")
            return False

    def get_by_id(self, session_id: str) -> Optional[dict]:
        if not db:
            return _OFFLINE_DB["workouts"].get(session_id)
        try:
            doc = db.collection("workouts").document(session_id).get()
            return {"id": doc.id, **doc.to_dict()} if doc.exists else None
        except Exception as e:
            print(f"WorkoutRepository.get_by_id error: {e}")
            return None

    def get_history(self, user_id: str) -> List[dict]:
        if not db:
            results = [w for w in _OFFLINE_DB["workouts"].values() if w.get("user_id") == user_id]
            results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return results
        try:
            docs = db.collection("workouts").where("user_id", "==", user_id).get()
            results = [{"id": doc.id, **doc.to_dict()} for doc in docs]
            # In-memory sorting to avoid composite index requirements
            results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return results
        except Exception as e:
            print(f"WorkoutRepository.get_history error: {e}")
            return []

    def get_leaderboard(self, period: str, limit: int) -> List[dict]:
        try:
            now = datetime.utcnow()
            if not db:
                workouts = list(_OFFLINE_DB["workouts"].values())
            else:
                docs = db.collection("workouts").get()
                workouts = [doc.to_dict() for doc in docs]

            grouped = {}
            for w in workouts:
                # Filter by timestamp manually
                ts_str = w.get("timestamp", "")
                if not ts_str: continue
                try:
                    # Parse timestamp format (standard ISO)
                    w_date = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                except ValueError:
                    continue

                if period == "daily" and (now - w_date).days >= 1:
                    continue
                elif period == "weekly" and (now - w_date).days >= 7:
                    continue

                uid = w.get("user_id")
                if not uid: continue
                
                if uid not in grouped:
                    grouped[uid] = {"total_reps": 0, "accuracy_sum": 0.0, "total_workouts": 0}
                grouped[uid]["total_reps"] += w.get("reps", 0)
                grouped[uid]["accuracy_sum"] += w.get("accuracy", 0.0)
                grouped[uid]["total_workouts"] += 1

            results = []
            for uid, stats in grouped.items():
                results.append({
                    "_id": uid,
                    "total_reps": stats["total_reps"],
                    "avg_accuracy": stats["accuracy_sum"] / stats["total_workouts"],
                    "total_workouts": stats["total_workouts"]
                })

            results.sort(key=lambda x: x["total_reps"], reverse=True)
            return results[:limit]
        except Exception as e:
            print(f"WorkoutRepository.get_leaderboard error: {e}")
            return []


class FriendRepository:
    def send_request(self, request_data: dict) -> dict:
        if not db:
            import uuid
            data = dict(request_data)
            data["id"] = data.get("id") or str(uuid.uuid4())
            _OFFLINE_DB["friend_requests"][data["id"]] = data
            return data
        try:
            doc_ref = db.collection("friend_requests").document()
            data = dict(request_data)
            data["id"] = doc_ref.id
            doc_ref.set(data)
            return data
        except Exception as e:
            print(f"FriendRepository.send_request error: {e}")
            raise e

    def get_request(self, request_id: str, to_username: str) -> Optional[dict]:
        if not db:
            req = _OFFLINE_DB["friend_requests"].get(request_id)
            if req and req.get("to_username") == to_username and req.get("status") == "pending":
                return req
            return None
        try:
            doc = db.collection("friend_requests").document(request_id).get()
            if doc.exists:
                data = doc.to_dict()
                if data.get("to_username") == to_username and data.get("status") == "pending":
                    return {"id": doc.id, **data}
            return None
        except Exception as e:
            print(f"FriendRepository.get_request error: {e}")
            return None

    def get_requests_for_user(self, username: str) -> List[dict]:
        if not db:
            return [r for r in _OFFLINE_DB["friend_requests"].values() if (r.get("to_username") == username or r.get("from_username") == username) and r.get("status") == "pending"]
        try:
            incoming = db.collection("friend_requests").where("to_username", "==", username).where("status", "==", "pending").get()
            outgoing = db.collection("friend_requests").where("from_username", "==", username).where("status", "==", "pending").get()
            
            results = []
            seen = set()
            for doc in incoming + outgoing:
                if doc.id not in seen:
                    seen.add(doc.id)
                    results.append({"id": doc.id, **doc.to_dict()})
            return results
        except Exception as e:
            print(f"FriendRepository.get_requests_for_user error: {e}")
            return []

    def respond_to_request(self, request_id: str, action: str) -> bool:
        if not db:
            if request_id in _OFFLINE_DB["friend_requests"]:
                _OFFLINE_DB["friend_requests"][request_id]["status"] = action
                _OFFLINE_DB["friend_requests"][request_id]["responded_at"] = datetime.utcnow().isoformat()
                return True
            return False
        try:
            db.collection("friend_requests").document(request_id).update({
                "status": action,
                "responded_at": datetime.utcnow().isoformat()
            })
            return True
        except Exception as e:
            print(f"FriendRepository.respond_to_request error: {e}")
            return False

    def create_friendship(self, friendship_data: dict) -> dict:
        if not db:
            import uuid
            data = dict(friendship_data)
            data["id"] = data.get("id") or str(uuid.uuid4())
            _OFFLINE_DB["friends"].append(data)
            return data
        try:
            doc_ref = db.collection("friends").document()
            data = dict(friendship_data)
            data["id"] = doc_ref.id
            doc_ref.set(data)
            return data
        except Exception as e:
            print(f"FriendRepository.create_friendship error: {e}")
            return friendship_data

    def get_friends(self, username: str) -> List[dict]:
        if not db:
            return [f for f in _OFFLINE_DB["friends"] if f.get("user1") == username or f.get("user2") == username]
        try:
            friends1 = db.collection("friends").where("user1", "==", username).get()
            friends2 = db.collection("friends").where("user2", "==", username).get()
            return [{"id": doc.id, **doc.to_dict()} for doc in friends1 + friends2]
        except Exception as e:
            print(f"FriendRepository.get_friends error: {e}")
            return []


class NotificationRepository:
    def get_all(self, user_id: str) -> List[dict]:
        if not db:
            results = [n for n in _OFFLINE_DB["notifications"].values() if n.get("user_id") == user_id]
            results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return results
        try:
            docs = db.collection("notifications").where("user_id", "==", user_id).get()
            results = [{"id": doc.id, **doc.to_dict()} for doc in docs]
            results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return results
        except Exception as e:
            print(f"NotificationRepository.get_all error: {e}")
            return []

    def create(self, notification_data: dict) -> dict:
        if not db:
            import uuid
            data = dict(notification_data)
            data["id"] = data.get("id") or str(uuid.uuid4())
            _OFFLINE_DB["notifications"][data["id"]] = data
            return data
        try:
            doc_ref = db.collection("notifications").document()
            data = dict(notification_data)
            data["id"] = doc_ref.id
            doc_ref.set(data)
            return data
        except Exception as e:
            print(f"NotificationRepository.create error: {e}")
            raise e

    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        if not db:
            n = _OFFLINE_DB["notifications"].get(notification_id)
            if n and n.get("user_id") == user_id:
                n["read"] = True
                return True
            return False
        try:
            doc_ref = db.collection("notifications").document(notification_id)
            doc = doc_ref.get()
            if doc.exists and doc.to_dict().get("user_id") == user_id:
                doc_ref.update({"read": True})
                return True
            return False
        except Exception as e:
            print(f"NotificationRepository.mark_as_read error: {e}")
            return False

    def delete(self, notification_id: str, user_id: str) -> bool:
        if not db:
            if notification_id in _OFFLINE_DB["notifications"] and _OFFLINE_DB["notifications"][notification_id].get("user_id") == user_id:
                del _OFFLINE_DB["notifications"][notification_id]
                return True
            return False
        try:
            doc_ref = db.collection("notifications").document(notification_id)
            doc = doc_ref.get()
            if doc.exists and doc.to_dict().get("user_id") == user_id:
                doc_ref.delete()
                return True
            return False
        except Exception as e:
            print(f"NotificationRepository.delete error: {e}")
            return False

    def count_unread(self, user_id: str) -> int:
        if not db:
            return sum(1 for n in _OFFLINE_DB["notifications"].values() if n.get("user_id") == user_id and not n.get("read", False))
        try:
            docs = db.collection("notifications").where("user_id", "==", user_id).where("read", "==", False).get()
            return len(docs)
        except Exception as e:
            print(f"NotificationRepository.count_unread error: {e}")
            return 0


class PointsRepository:
    def get_by_user(self, user_id: str) -> Optional[dict]:
        if not db:
            for p in _OFFLINE_DB["user_points"].values():
                if p.get("user_id") == user_id:
                    return p
            return None
        try:
            docs = db.collection("user_points").where("user_id", "==", user_id).limit(1).get()
            return {"id": docs[0].id, **docs[0].to_dict()} if docs else None
        except Exception as e:
            print(f"PointsRepository.get_by_user error: {e}")
            return None

    def create(self, points_data: dict) -> dict:
        if not db:
            import uuid
            data = dict(points_data)
            data["id"] = data.get("id") or str(uuid.uuid4())
            _OFFLINE_DB["user_points"][data["id"]] = data
            return data
        try:
            doc_ref = db.collection("user_points").document()
            data = dict(points_data)
            data["id"] = doc_ref.id
            doc_ref.set(data)
            return data
        except Exception as e:
            print(f"PointsRepository.create error: {e}")
            return points_data

    def update_points(self, user_id: str, total_points: int, exercise_points: dict) -> bool:
        if not db:
            for p in _OFFLINE_DB["user_points"].values():
                if p.get("user_id") == user_id:
                    p["total_points"] = total_points
                    p["exercise_points"] = exercise_points
                    p["last_updated"] = datetime.utcnow().isoformat()
                    return True
            return False
        try:
            docs = db.collection("user_points").where("user_id", "==", user_id).limit(1).get()
            if docs:
                docs[0].reference.update({
                    "total_points": total_points,
                    "exercise_points": exercise_points,
                    "last_updated": datetime.utcnow().isoformat()
                })
                return True
            return False
        except Exception as e:
            print(f"PointsRepository.update_points error: {e}")
            return False

    def get_leaderboard(self, limit: int) -> List[dict]:
        if not db:
            results = list(_OFFLINE_DB["user_points"].values())
            results.sort(key=lambda x: x.get("total_points", 0), reverse=True)
            return results[:limit]
        try:
            docs = db.collection("user_points").get()
            results = [{"id": doc.id, **doc.to_dict()} for doc in docs]
            results.sort(key=lambda x: x.get("total_points", 0), reverse=True)
            return results[:limit]
        except Exception as e:
            print(f"PointsRepository.get_leaderboard error: {e}")
            return []

    def get_friends_points(self, friend_ids: List[str]) -> List[dict]:
        if not friend_ids: return []
        if not db:
            return [p for p in _OFFLINE_DB["user_points"].values() if p.get("user_id") in friend_ids]
        try:
            results = []
            for i in range(0, len(friend_ids), 30):
                chunk = friend_ids[i:i+30]
                docs = db.collection("user_points").where("user_id", "in", chunk).get()
                results.extend([{"id": doc.id, **doc.to_dict()} for doc in docs])
            return results
        except Exception as e:
            print(f"PointsRepository.get_friends_points error: {e}")
            return []

    def create_history_record(self, record_data: dict) -> dict:
        if not db:
            import uuid
            data = dict(record_data)
            data["id"] = data.get("id") or str(uuid.uuid4())
            _OFFLINE_DB["points_history"].append(data)
            return data
        try:
            doc_ref = db.collection("points_history").document()
            data = dict(record_data)
            data["id"] = doc_ref.id
            doc_ref.set(data)
            return data
        except Exception as e:
            print(f"PointsRepository.create_history_record error: {e}")
            return record_data

    def get_history(self, user_id: str, exercise: Optional[str] = None, limit: int = 20) -> List[dict]:
        if not db:
            results = [r for r in _OFFLINE_DB["points_history"] if r.get("user_id") == user_id]
            if exercise:
                results = [r for r in results if r.get("exercise") == exercise]
            results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return results[:limit]
        try:
            query = db.collection("points_history").where("user_id", "==", user_id)
            if exercise:
                query = query.where("exercise", "==", exercise)
            docs = query.get()
            results = [{"id": doc.id, **doc.to_dict()} for doc in docs]
            results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return results[:limit]
        except Exception as e:
            print(f"PointsRepository.get_history error: {e}")
            return []


class SessionRepository:
    def create(self, session_data: dict) -> dict:
        if not db:
            import uuid
            data = dict(session_data)
            data["id"] = data.get("id") or str(uuid.uuid4())
            _OFFLINE_DB["sessions"][data["id"]] = data
            return data
        try:
            doc_ref = db.collection("sessions").document()
            data = dict(session_data)
            data["id"] = doc_ref.id
            doc_ref.set(data)
            return data
        except Exception as e:
            print(f"SessionRepository.create error: {e}")
            return session_data


user_repository = UserRepository()
workout_repository = WorkoutRepository()
friend_repository = FriendRepository()
notification_repository = NotificationRepository()
points_repository = PointsRepository()
session_repository = SessionRepository()
