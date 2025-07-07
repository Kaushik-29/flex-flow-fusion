import React, { useRef, useEffect, useState } from "react";
import Webcam from "react-webcam";
import * as poseDetection from "@tensorflow-models/pose-detection";
import "@tensorflow/tfjs-backend-webgl";

const videoWidth = 640;
const videoHeight = 480;

// Keypoint interface
interface Keypoint {
  x: number;
  y: number;
  score?: number;
  name?: string;
}

// Shared exercise state
interface ExerciseState {
  inPosition: boolean;
  lastRepTime: number;
  consecutiveFrames: number;
}

interface PoseDetectorProps {
  isDetecting: boolean;
  exercise: string;
  onRepDetected: (keypoints: Keypoint[], repCount: number) => void;
}

// Calculate angle between 3 points
function getAngle(a: { x: number; y: number }, b: { x: number; y: number }, c: { x: number; y: number }) {
  const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
  let angle = Math.abs(radians * 180.0 / Math.PI);
  if (angle > 180.0) angle = 360 - angle;
  return angle;
}

const PoseDetector: React.FC<PoseDetectorProps> = ({ isDetecting, exercise, onRepDetected }) => {
  const webcamRef = useRef<Webcam>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [repCount, setRepCount] = useState(0);

  const exerciseState = useRef<ExerciseState>({
    inPosition: false,
    lastRepTime: 0,
    consecutiveFrames: 0,
  });

  // Reset state when exercise changes or detection stops
  useEffect(() => {
    exerciseState.current = {
      inPosition: false,
      lastRepTime: 0,
      consecutiveFrames: 0,
    };
    setRepCount(0);
    console.log("Exercise state reset");
  }, [exercise, isDetecting]);

  useEffect(() => {
    let detector: poseDetection.PoseDetector;
    let rafId: number;

    const runPose = async () => {
      try {
        detector = await poseDetection.createDetector(
          poseDetection.SupportedModels.MoveNet,
          { modelType: poseDetection.movenet.modelType.SINGLEPOSE_LIGHTNING }
        );
        console.log("Pose detector loaded");
        detectLoop();
      } catch (error) {
        console.error("Failed to create pose detector:", error);
      }
    };

    const detectLoop = async () => {
      if (!isDetecting) {
        rafId = requestAnimationFrame(detectLoop);
        return;
      }

      const video = webcamRef.current?.video as HTMLVideoElement;
      if (!video || video.readyState !== 4) {
        rafId = requestAnimationFrame(detectLoop);
        return;
      }

      try {
        const poses = await detector.estimatePoses(video);
        const ctx = canvasRef.current?.getContext("2d");

        if (ctx && poses[0]?.keypoints) {
          ctx.clearRect(0, 0, videoWidth, videoHeight);
          drawKeypoints(poses[0].keypoints, ctx);

          const keypoints = poses[0].keypoints;
          const currentTime = Date.now();

          // Normalize exercise name
          const normalizedExercise = exercise.toLowerCase().replace(/[-_ ]/g, "");

          if (normalizedExercise.includes("squat")) {
            detectSquat(keypoints, currentTime);
          } else if (normalizedExercise.includes("pushup")) {
            detectPushup(keypoints, currentTime);
          }
        }
      } catch (error) {
        console.error("Detection error:", error);
      }

      rafId = requestAnimationFrame(detectLoop);
    };

    runPose();

    return () => {
      if (rafId) cancelAnimationFrame(rafId);
      if (detector) detector.dispose();
    };
  }, [isDetecting, exercise]);

  // Squat detection logic
  const detectSquat = (keypoints: Keypoint[], currentTime: number) => {
    const leftHip = keypoints.find(k => k.name === "left_hip");
    const leftKnee = keypoints.find(k => k.name === "left_knee");
    const leftAnkle = keypoints.find(k => k.name === "left_ankle");

    if (!leftHip || !leftKnee || !leftAnkle ||
      (leftHip.score || 0) < 0.3 ||
      (leftKnee.score || 0) < 0.3 ||
      (leftAnkle.score || 0) < 0.3) return;

    const kneeAngle = getAngle(leftHip, leftKnee, leftAnkle);
    console.log(`Squat angle: ${kneeAngle.toFixed(1)}`);

    if (kneeAngle < 100 && !exerciseState.current.inPosition) {
      exerciseState.current.inPosition = true;
      exerciseState.current.consecutiveFrames = 0;
      console.log("Squat: Down position entered");
    } else if (kneeAngle > 150 && exerciseState.current.inPosition) {
      exerciseState.current.consecutiveFrames++;
      if (exerciseState.current.consecutiveFrames >= 3) {
        if (currentTime - exerciseState.current.lastRepTime > 1000) {
          completeRep(keypoints, currentTime);
          console.log("Squat: Rep completed");
        }
        exerciseState.current.inPosition = false;
        exerciseState.current.consecutiveFrames = 0;
      }
    } else if (kneeAngle > 150) {
      exerciseState.current.consecutiveFrames = 0;
    }
  };

  // Push-up detection logic
  const detectPushup = (keypoints: Keypoint[], currentTime: number) => {
    const leftShoulder = keypoints.find(k => k.name === 'left_shoulder');
    const leftElbow = keypoints.find(k => k.name === 'left_elbow');
    const leftWrist = keypoints.find(k => k.name === 'left_wrist');
  
    if (
      !leftShoulder || !leftElbow || !leftWrist ||
      (leftShoulder.score ?? 0) < 0.3 ||
      (leftElbow.score ?? 0) < 0.3 ||
      (leftWrist.score ?? 0) < 0.3
    ) return;
  
    const elbowAngle = getAngle(leftShoulder, leftElbow, leftWrist);
  
    console.log(`Push-up angle: ${elbowAngle.toFixed(1)}, inPosition: ${exerciseState.current.inPosition}, frames: ${exerciseState.current.consecutiveFrames}`);
  
    if (elbowAngle < 90 && !exerciseState.current.inPosition) {
      exerciseState.current.inPosition = true;
      exerciseState.current.consecutiveFrames = 0;
      console.log("Push-up: Down position entered");
    } else if (elbowAngle > 150 && exerciseState.current.inPosition) {
      exerciseState.current.consecutiveFrames++;
      if (exerciseState.current.consecutiveFrames >= 2) {
        if (currentTime - exerciseState.current.lastRepTime > 800) {
          completeRep(keypoints, currentTime);
          console.log("Push-up: Rep completed!");
          exerciseState.current.lastRepTime = currentTime;
        }
        exerciseState.current.inPosition = false;
        exerciseState.current.consecutiveFrames = 0;
      }
    } else if (elbowAngle > 150) {
      exerciseState.current.consecutiveFrames = 0;
    }
  };
  

  // Rep completion logic
  const completeRep = (keypoints: Keypoint[], currentTime: number) => {
    setRepCount(r => {
      const newCount = r + 1;
      onRepDetected(keypoints, newCount);
      return newCount;
    });
    exerciseState.current.lastRepTime = currentTime;
  };

  // Draw keypoints on canvas
  const drawKeypoints = (keypoints: Keypoint[], ctx: CanvasRenderingContext2D) => {
    keypoints.forEach(keypoint => {
      if (keypoint && keypoint.x != null && keypoint.y != null && (keypoint.score ?? 0) > 0.3) {
        ctx.beginPath();
        ctx.arc(keypoint.x, keypoint.y, 5, 0, 2 * Math.PI);
        ctx.fillStyle = "red";
        ctx.fill();
      }
    });
  };

  return (
    <div style={{ position: "relative", width: videoWidth, height: videoHeight }}>
      <Webcam
        ref={webcamRef}
        width={videoWidth}
        height={videoHeight}
        style={{ position: "absolute", left: 0, top: 0 }}
        mirrored
      />
      <canvas
        ref={canvasRef}
        width={videoWidth}
        height={videoHeight}
        style={{ position: "absolute", left: 0, top: 0 }}
      />
    </div>
  );
};

export default PoseDetector;
