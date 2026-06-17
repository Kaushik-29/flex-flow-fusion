from fastapi import APIRouter, Request
from app.models import Keypoint, PoseFeedbackRequest, PoseFeedbackResponse, Session
from app.db import session_repository
from typing import List
import math
from datetime import datetime

router = APIRouter()

def calculate_angle(a, b, c):
    ang = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) -
        math.atan2(a[1] - b[1], a[0] - b[0])
    )
    ang = abs(ang)
    if ang > 180:
        ang = 360 - ang
    return ang

def analyze_squat(keypoints):
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
    if len(keypoints) < 6:
        return "Insufficient keypoints for lunge analysis", 0.5

    left_angle = calculate_angle(
        (keypoints[0].x, keypoints[0].y),
        (keypoints[1].x, keypoints[1].y),
        (keypoints[2].x, keypoints[2].y)
    )

    right_angle = calculate_angle(
        (keypoints[3].x, keypoints[3].y),
        (keypoints[4].x, keypoints[4].y),
        (keypoints[5].x, keypoints[5].y)
    )

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
    if len(keypoints) < 6:
        return "Insufficient keypoints for jumping jack analysis", 0.5

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
    if len(keypoints) < 4:
        return "Insufficient keypoints for plank analysis", 0.5

    shoulder = (keypoints[0].x, keypoints[0].y)
    ankle = (keypoints[3].x, keypoints[3].y)

    body_angle = abs(shoulder[1] - ankle[1])

    if body_angle < 20:
        return "Perfect plank! Keep your body straight and core engaged.", 0.9
    elif body_angle < 40:
        return "Good form! Keep your hips level and body straight.", 0.8
    else:
        return "Straighten your body. Keep your hips in line with shoulders and ankles.", 0.6

def analyze_mountain_climber(keypoints):
    if len(keypoints) < 4:
        return "Insufficient keypoints for mountain climber analysis", 0.5

    left_hip = (keypoints[0].x, keypoints[0].y)
    left_knee = (keypoints[1].x, keypoints[1].y)
    right_hip = (keypoints[2].x, keypoints[2].y)
    right_knee = (keypoints[3].x, keypoints[3].y)

    left_knee_height = left_hip[1] - left_knee[1]
    right_knee_height = right_hip[1] - right_knee[1]

    if abs(left_knee_height - right_knee_height) > 30:
        return "Great mountain climber! Keep alternating legs with good form.", 0.9
    else:
        return "Alternate your legs more distinctly. Drive your knees toward your chest.", 0.7

def analyze_high_knees(keypoints):
    if len(keypoints) < 4:
        return "Insufficient keypoints for high knees analysis", 0.5

    left_hip = (keypoints[0].x, keypoints[0].y)
    left_knee = (keypoints[1].x, keypoints[1].y)
    right_hip = (keypoints[2].x, keypoints[2].y)
    right_knee = (keypoints[3].x, keypoints[3].y)

    left_knee_height = left_hip[1] - left_knee[1]
    right_knee_height = right_hip[1] - right_knee[1]

    if left_knee_height > 50 or right_knee_height > 50:
        return "Excellent high knees! Keep driving your knees up high.", 0.9
    else:
        return "Lift your knees higher! Aim to bring them to waist level.", 0.7

def analyze_burpee(keypoints):
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
    return {"tips": ["Exercise analysis working"], "score": 0.8}

def get_pose_feedback(keypoints):
    return "Pose detected"

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
    session_dict = session.dict()
    session_dict["timestamp"] = session_dict["timestamp"].isoformat()
    session_repository.create(session_dict)
    return {"feedback": feedback}
