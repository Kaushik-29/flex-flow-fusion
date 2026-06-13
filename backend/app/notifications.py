from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from .db import get_database
from .auth import get_current_user
from bson import ObjectId

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

class FriendRequestCreate(BaseModel):
    from_username: str
    to_username: str

class FriendRequestResponse(BaseModel):
    id: str
    from_username: str
    to_username: str
    timestamp: datetime
    status: str

@router.get("/", response_model=List[Notification])
async def get_notifications(current_user = Depends(get_current_user)):
    """Get all notifications for the current user"""
    db = get_database()
    notifications = db["notifications"]
    
    # Get notifications for the current user
    user_notifications = list(notifications.find({
        "user_id": current_user.get("username")
    }).sort("created_at", -1))
    
    # Format the data
    def format_notification(notif):
        notif["id"] = str(notif["_id"])
        del notif["_id"]
        # Handle both timestamp and created_at fields
        if "timestamp" in notif and "created_at" not in notif:
            notif["created_at"] = notif["timestamp"]
        return notif
    
    return [format_notification(notif) for notif in user_notifications]

@router.post("/", response_model=Notification)
async def create_notification(
    notification: NotificationCreate,
    current_user = Depends(get_current_user)
):
    """Create a new notification"""
    db = get_database()
    notifications = db["notifications"]
    
    notification_data = {
        "user_id": current_user.get("username"),
        "type": notification.type,
        "title": notification.title,
        "message": notification.message,
        "data": notification.data,
        "read": False,
        "created_at": datetime.utcnow()
    }
    
    result = notifications.insert_one(notification_data)
    
    # Get the created notification to return the full object
    created_notification = notifications.find_one({"_id": result.inserted_id})
    if created_notification:
        created_notification["id"] = str(created_notification["_id"])
        del created_notification["_id"]
        return created_notification
    else:
        raise HTTPException(status_code=500, detail="Failed to create notification")

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user = Depends(get_current_user)
):
    """Mark a notification as read"""
    db = get_database()
    notifications = db["notifications"]
    
    # Update the notification
    result = notifications.update_one(
        {
            "_id": ObjectId(notification_id),
            "user_id": current_user.get("username")
        },
        {"$set": {"read": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user = Depends(get_current_user)
):
    """Delete a notification"""
    db = get_database()
    notifications = db["notifications"]
    
    result = notifications.delete_one({
        "_id": ObjectId(notification_id),
        "user_id": current_user.get("username")
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification deleted successfully"}

# Friend Requests endpoints
@router.get("/friend-requests")
async def get_friend_requests_notifications(current_user=Depends(get_current_user)):
    """Get friend request notifications"""
    db = get_database()
    friend_requests = db["friend_requests"]
    
    # Get incoming friend requests
    incoming_requests = list(friend_requests.find({
        "to_username": current_user.get("username"),
        "status": "pending"
    }))
    
    # Convert to notification format
    notifications = []
    for request in incoming_requests:
        # Handle both timestamp and created_at fields
        created_at = request.get("created_at", request.get("timestamp"))
        notifications.append({
            "id": str(request["_id"]),
            "type": "friend_request",
            "title": "New Friend Request",
            "message": f"{request['from_username']} sent you a friend request",
            "data": {
                "from_username": request["from_username"],
                "request_id": str(request["_id"]),
                "created_at": created_at.isoformat() if created_at else None
            },
            "read": False,
            "created_at": created_at
        })
    
    return notifications

@router.get("/unread-count")
async def get_unread_count(current_user=Depends(get_current_user)):
    """Get count of unread notifications"""
    db = get_database()
    notifications = db["notifications"]
    
    count = notifications.count_documents({
        "user_id": current_user.get("username"),
        "read": False
    })
    
    return {"unread_count": count} 