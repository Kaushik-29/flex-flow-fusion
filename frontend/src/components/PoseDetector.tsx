import React, { useRef, useEffect, useState } from "react";
import Webcam from "react-webcam";
import * as poseDetection from "@tensorflow-models/pose-detection";
import "@tensorflow/tfjs-backend-webgl";

const videoWidth = 640;
const videoHeight = 480;

// Simple interface for keypoints
interface Keypoint {
  x: number;
  y: number;
  score?: number;
  name?: string;
}

// Simple state for squat detection only
interface SquatState {
  inSquatPosition: boolean;
  lastRepTime: number;
  consecutiveFrames: number;
}

interface PoseDetectorProps {
  isDetecting: boolean;
  exercise: string;
  onRepDetected: (keypoints: Keypoint[], repCount: number) => void;
}

// Calculate angle between three points
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

  // Simple squat state
  const squatState = useRef<SquatState>({
    inSquatPosition: false,
    lastRepTime: 0,
    consecutiveFrames: 0,
  });

  // Reset state when exercise changes or detection stops
  useEffect(() => {
    squatState.current = {
      inSquatPosition: false,
      lastRepTime: 0,
      consecutiveFrames: 0,
    };
    setRepCount(0);
    console.log("Squat state reset");
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
        console.error('Failed to create pose detector:', error);
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
          
          // ONLY detect squat - ignore other exercises
          if (exercise.toLowerCase().includes('squat')) {
            detectSquat(keypoints, currentTime);
          }
        }
      } catch (error) {
        console.error('Detection error:', error);
      }
      
      rafId = requestAnimationFrame(detectLoop);
    };

    runPose();

    return () => {
      if (rafId) cancelAnimationFrame(rafId);
      if (detector) detector.dispose();
    };
  }, [isDetecting, exercise]);

  // SIMPLE SQUAT DETECTION ONLY
  const detectSquat = (keypoints: Keypoint[], currentTime: number) => {
    // Find the keypoints we need for squat detection
    const leftHip = keypoints.find(k => k.name === 'left_hip');
    const leftKnee = keypoints.find(k => k.name === 'left_knee');
    const leftAnkle = keypoints.find(k => k.name === 'left_ankle');
    
    // Check if we have all required keypoints with good confidence
    if (!leftHip || !leftKnee || !leftAnkle || 
        (leftHip.score || 0) < 0.3 || 
        (leftKnee.score || 0) < 0.3 || 
        (leftAnkle.score || 0) < 0.3) {
      return;
    }

    // Calculate knee angle
    const kneeAngle = getAngle(leftHip, leftKnee, leftAnkle);
    
    console.log(`Squat angle: ${kneeAngle.toFixed(1)}, In position: ${squatState.current.inSquatPosition}`);
    
    // Simple squat logic:
    // - If knee angle < 100 degrees, we're in squat position
    // - If knee angle > 150 degrees, we're standing
    // - Need to go from standing -> squat -> standing to count a rep
    
    if (kneeAngle < 100 && !squatState.current.inSquatPosition) {
      // Entered squat position
      squatState.current.inSquatPosition = true;
      squatState.current.consecutiveFrames = 0;
      console.log("Squat: Entered down position");
    } else if (kneeAngle > 150 && squatState.current.inSquatPosition) {
      // Came back up from squat
      squatState.current.consecutiveFrames++;
      
      // Need to stay up for a few frames to confirm the rep
      if (squatState.current.consecutiveFrames >= 3) {
        // Check cooldown to prevent multiple reps
        if (currentTime - squatState.current.lastRepTime > 1000) { // 1 second cooldown
          console.log("Squat: Rep completed!");
          completeRep(keypoints, currentTime);
          squatState.current.lastRepTime = currentTime;
        }
        squatState.current.inSquatPosition = false;
        squatState.current.consecutiveFrames = 0;
      }
    } else if (kneeAngle > 150) {
      // Reset consecutive frames if we're standing
      squatState.current.consecutiveFrames = 0;
    }
  };

  // Simple rep completion
  const completeRep = (keypoints: Keypoint[], currentTime: number) => {
    setRepCount(r => {
      const newCount = r + 1;
      onRepDetected(keypoints, newCount);
      console.log(`Squat rep ${newCount} completed!`);
      return newCount;
    });
  };

  // Draw keypoints on canvas
  function drawKeypoints(keypoints: Keypoint[], ctx: CanvasRenderingContext2D) {
    if (!ctx) return;
    keypoints.forEach((keypoint) => {
      if (keypoint && keypoint.x != null && keypoint.y != null && (keypoint.score ?? 0) > 0.3) {
        ctx.beginPath();
        ctx.arc(keypoint.x, keypoint.y, 5, 0, 2 * Math.PI);
        ctx.fillStyle = "red";
        ctx.fill();
      }
    });
  }

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