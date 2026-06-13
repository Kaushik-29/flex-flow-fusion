import cv2
import mediapipe as mp
import time

# Initialize MediaPipe pose class and drawing utils
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# For webcam input:
cap = cv2.VideoCapture(0)

# Initialize pose estimator
with mp_pose.Pose(
    static_image_mode=False,
    model_complexity=1,
    enable_segmentation=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
) as pose:

    prev_time = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Ignoring empty camera frame.")
            break

        # Convert the BGR image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Process the image and find pose
        results = pose.process(image)

        # Draw the pose annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0,0,255), thickness=2, circle_radius=2)
            )

        # Calculate and display FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time

        cv2.putText(image, f'FPS: {int(fps)}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.imshow('MediaPipe Pose - Press q to Quit', image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows() 