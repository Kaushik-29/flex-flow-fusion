from fastapi import APIRouter, Request
from app.models import Keypoint, PoseFeedbackRequest, PoseFeedbackResponse, get_db, Session
from typing import List
import math
from datetime import datetime

router = APIRouter()

def calculate_angle(a, b, c):
    # Calculate angle at point b given three points
    ang = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    )
    ang = abs(ang)
    if ang > 180:
        ang = 360 - ang
    return ang

def analyze_squat(keypoints):
    """Analyze squat form using hip, knee, ankle angles"""
    if len(keypoints) < 3:
        return "Insufficient keypoints for squat analysis", 0.5
    
    hip = (keypoints[0].x, keypoints[0].y)
    knee = (keypoints[1].x, keypoints[1].y)
    ankle = (keypoints[2].x, keypoints[2].y)
    angle = calculate_angle(hip, knee, ankle)
    
    if angle < 70:
        return "Great depth! Keep your chest up and knees aligned with toes.", 0.9
    elif angle < 90:
        return "Good form! Try to go a bit deeper for better results.", 0.8
    elif angle < 120:
        return "Keep going lower! Your knees should be at 90 degrees.", 0.6
    else:
        return "Stand up straight and prepare for the next squat.", 0.7

def analyze_pushup(keypoints):
    """Analyze push-up form using shoulder, elbow, wrist angles"""
    if len(keypoints) < 3:
        return "Insufficient keypoints for push-up analysis", 0.5
    
    shoulder = (keypoints[0].x, keypoints[0].y)
    elbow = (keypoints[1].x, keypoints[1].y)
    wrist = (keypoints[2].x, keypoints[2].y)
    angle = calculate_angle(shoulder, elbow, wrist)
    
    if angle < 90:
        return "Perfect form! Keep your body straight and controlled.", 0.9
    elif angle < 120:
        return "Good! Lower yourself more for a complete push-up.", 0.8
    elif angle < 150:
        return "Keep your elbows close to your body and go lower.", 0.6
    else:
        return "Maintain a straight body line and prepare for the next rep.", 0.7

def analyze_lunge(keypoints):
    """Analyze lunge form using hip, knee, ankle angles"""
    if len(keypoints) < 6:
        return "Insufficient keypoints for lunge analysis", 0.5
    
    # Use the leg with the deeper angle
    left_angle = calculate_angle((keypoints[0].x, keypoints[0].y), 
                               (keypoints[1].x, keypoints[1].y), 
                               (keypoints[2].x, keypoints[2].y))
    right_angle = calculate_angle((keypoints[3].x, keypoints[3].y), 
                                (keypoints[4].x, keypoints[4].y), 
                                (keypoints[5].x, keypoints[5].y))
    
    angle = min(left_angle, right_angle)
    
    if angle < 80:
        return "Excellent lunge depth! Keep your front knee over your ankle.", 0.9
    elif angle < 100:
        return "Good form! Try to go deeper for maximum benefit.", 0.8
    elif angle < 130:
        return "Lower your body more. Your front thigh should be parallel to the ground.", 0.6
    else:
        return "Step forward and lower into the lunge position.", 0.7

def analyze_jumping_jack(keypoints):
    """Analyze jumping jack form using arm and leg positions"""
    if len(keypoints) < 6:
        return "Insufficient keypoints for jumping jack analysis", 0.5
    
    # Check arm and leg spread
    left_wrist = (keypoints[0].x, keypoints[0].y)
    right_wrist = (keypoints[1].x, keypoints[1].y)
    left_shoulder = (keypoints[2].x, keypoints[2].y)
    right_shoulder = (keypoints[3].x, keypoints[3].y)
    
    arm_spread = abs(left_wrist[0] - right_wrist[0])
    shoulder_width = abs(left_shoulder[0] - right_shoulder[0])
    
    if arm_spread > shoulder_width * 1.5:
        return "Perfect jumping jack! Arms and legs are fully extended.", 0.9
    elif arm_spread > shoulder_width * 1.2:
        return "Good form! Try to extend your arms and legs more.", 0.8
    else:
        return "Extend your arms overhead and legs apart for a proper jumping jack.", 0.6

def analyze_plank(keypoints):
    """Analyze plank form using body alignment"""
    if len(keypoints) < 4:
        return "Insufficient keypoints for plank analysis", 0.5
    
    shoulder = (keypoints[0].x, keypoints[0].y)
    elbow = (keypoints[1].x, keypoints[1].y)
    hip = (keypoints[2].x, keypoints[2].y)
    ankle = (keypoints[3].x, keypoints[3].y)
    
    # Check if body is straight
    body_angle = abs(shoulder[1] - ankle[1])
    if body_angle < 20:
        return "Perfect plank! Keep your body straight and core engaged.", 0.9
    elif body_angle < 40:
        return "Good form! Keep your hips level and body straight.", 0.8
    else:
        return "Straighten your body. Keep your hips in line with shoulders and ankles.", 0.6

def analyze_mountain_climber(keypoints):
    """Analyze mountain climber form using knee positions"""
    if len(keypoints) < 4:
        return "Insufficient keypoints for mountain climber analysis", 0.5
    
    left_hip = (keypoints[0].x, keypoints[0].y)
    left_knee = (keypoints[1].x, keypoints[1].y)
    right_hip = (keypoints[2].x, keypoints[2].y)
    right_knee = (keypoints[3].x, keypoints[3].y)
    
    left_knee_height = left_hip[1] - left_knee[1]
    right_knee_height = right_hip[1] - right_knee[1]
    alternating = abs(left_knee_height - right_knee_height) > 30
    
    if alternating:
        return "Great mountain climber! Keep alternating legs with good form.", 0.9
    else:
        return "Alternate your legs more distinctly. Drive your knees toward your chest.", 0.7

def analyze_high_knees(keypoints):
    """Analyze high knees form using knee height"""
    if len(keypoints) < 4:
        return "Insufficient keypoints for high knees analysis", 0.5
    
    left_hip = (keypoints[0].x, keypoints[0].y)
    left_knee = (keypoints[1].x, keypoints[1].y)
    right_hip = (keypoints[2].x, keypoints[2].y)
    right_knee = (keypoints[3].x, keypoints[3].y)
    
    left_knee_height = left_hip[1] - left_knee[1]
    right_knee_height = right_hip[1] - right_knee[1]
    high_knee = left_knee_height > 50 or right_knee_height > 50
    
    if high_knee:
        return "Excellent high knees! Keep driving your knees up high.", 0.9
    else:
        return "Lift your knees higher! Aim to bring them to waist level.", 0.7

def analyze_burpee(keypoints):
    """Analyze burpee form using squat and standing positions"""
    if len(keypoints) < 4:
        return "Insufficient keypoints for burpee analysis", 0.5
    
    hip = (keypoints[0].x, keypoints[0].y)
    knee = (keypoints[1].x, keypoints[1].y)
    ankle = (keypoints[2].x, keypoints[2].y)
    shoulder = (keypoints[3].x, keypoints[3].y)
    
    squat_angle = calculate_angle(hip, knee, ankle)
    is_standing = shoulder[1] > hip[1]
    
    if squat_angle < 90 and not is_standing:
        return "Great burpee squat! Now jump up explosively.", 0.9
    elif is_standing and squat_angle > 150:
        return "Perfect landing! Control your descent for the next rep.", 0.8
    else:
        return "Squat down, jump up, and land softly for a complete burpee.", 0.7

@router.post("/pose-feedback")
def pose_feedback(data: PoseFeedbackRequest):
    pose_type = data.pose_type.lower()
    
    if pose_type == "squat" or pose_type == "jump squat":
        feedback, score = analyze_squat(data.keypoints)
    elif pose_type == "push-up":
        feedback, score = analyze_pushup(data.keypoints)
    elif pose_type == "forward lunge" or pose_type == "side lunge":
        feedback, score = analyze_lunge(data.keypoints)
    elif pose_type == "jumping jack":
        feedback, score = analyze_jumping_jack(data.keypoints)
    elif pose_type == "plank":
        feedback, score = analyze_plank(data.keypoints)
    elif pose_type == "mountain climber":
        feedback, score = analyze_mountain_climber(data.keypoints)
    elif pose_type == "high knees":
        feedback, score = analyze_high_knees(data.keypoints)
    elif pose_type == "burpee":
        feedback, score = analyze_burpee(data.keypoints)
    else:
        feedback = f"Exercise '{pose_type}' not yet supported. Keep up the good work!"
        score = 0.8
    
    return {"tips": [feedback], "score": score}

def get_pose_feedback(keypoints):
    # Example: check if knee is bent enough for a squat
    # (Replace with ML model inference if available)
    left_knee = next((k for k in keypoints if k.get('name') == 'left_knee'), None)
    left_hip = next((k for k in keypoints if k.get('name') == 'left_hip'), None)
    left_ankle = next((k for k in keypoints if k.get('name') == 'left_ankle'), None)
    if left_knee and left_hip and left_ankle:
        # Simple rule: y distance between hip and knee
        if abs(left_hip['y'] - left_knee['y']) < 30:
            return "Good squat!"
        else:
            return "Go lower!"
    return "Pose not detected"

@router.post("/pose-feedback-json")
async def pose_feedback_json(request: Request):
    data = await request.json()
    keypoints = data.get("keypoints")
    user_id = data.get("user_id", "anonymous")
    feedback = get_pose_feedback(keypoints)
    session = Session(
        user_id=user_id,
        timestamp=datetime.utcnow(),
        feedback=feedback,
        keypoints=keypoints
    )
    db = get_db()
    db.sessions.insert_one(session.dict())
    return {"feedback": feedback} 