from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.db import notification_repository, friend_repository
from app.auth import get_current_user

router = APIRouter(tags=["notifications"])

class NotificationCreate(BaseModel):
    type: str
    title: str
    message: str
    data: Optional[dict] = None

class Notification(BaseModel):
    id: str
    user_id: str
    type: str
    title: str
    message: str
    data: Optional[dict] = None
    read: bool = False
    created_at: datetime

@router.get("/", response_model=List[Notification])
async def get_notifications(current_user = Depends(get_current_user)):
    """Get all notifications for the current user"""
    username = current_user.get("username")
    user_notifications = notification_repository.get_all(username)
    
    # Format the data
    for notif in user_notifications:
        notif["id"] = str(notif["id"])
    
    return user_notifications

@router.post("/", response_model=Notification)
async def create_notification(
    notification: NotificationCreate,
    current_user = Depends(get_current_user)
):
    """Create a new notification"""
    notification_data = {
        "user_id": current_user.get("username"),
        "type": notification.type,
        "title": notification.title,
        "message": notification.message,
        "data": notification.data,
        "read": False,
        "created_at": datetime.utcnow().isoformat()
    }
    
    try:
        created = notification_repository.create(notification_data)
        created["id"] = str(created["id"])
        return created
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create notification")

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user = Depends(get_current_user)
):
    """Mark a notification as read"""
    success = notification_repository.mark_as_read(notification_id, current_user.get("username"))
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user = Depends(get_current_user)
):
    """Delete a notification"""
    success = notification_repository.delete(notification_id, current_user.get("username"))
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification deleted successfully"}

# Friend Requests endpoints
@router.get("/friend-requests")
async def get_friend_requests_notifications(current_user=Depends(get_current_user)):
    """Get friend request notifications"""
    username = current_user.get("username")
    requests = friend_repository.get_requests_for_user(username)
    
    notifications = []
    for req in requests:
        if req["to_username"] == username:
            created_at = req.get("created_at")
            notifications.append({
                "id": str(req["id"]),
                "type": "friend_request",
                "title": "New Friend Request",
                "message": f"{req['from_username']} sent you a friend request",
                "data": {
                    "from_username": req["from_username"],
                    "request_id": str(req["id"]),
                    "created_at": created_at if isinstance(created_at, str) else created_at.isoformat() if created_at else None
                },
                "read": False,
                "created_at": created_at
            })
    
    return notifications

@router.get("/unread-count")
async def get_unread_count(current_user=Depends(get_current_user)):
    """Get count of unread notifications"""
    count = notification_repository.count_unread(current_user.get("username"))
    return {"unread_count": count}