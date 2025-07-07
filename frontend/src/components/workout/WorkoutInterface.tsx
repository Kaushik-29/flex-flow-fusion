import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Timer, Zap, Heart, Settings, CheckCircle, Loader2, Coffee, Play } from "lucide-react";
import { workoutAPI, poseFeedbackAPI, pointsAPI } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import PoseDetector from "../PoseDetector";
import { calculateCycles, getRepsInCurrentCycle, getRepsToNextCycle, isCycleComplete, getExerciseConfig } from "@/lib/exercise-config";

export const WorkoutInterface = ({ user }: { user?: any }) => {
  const [isDetecting, setIsDetecting] = useState(false);
  const [exerciseMode, setExerciseMode] = useState("analysis"); // "analysis" or "custom"
  const [currentExercise, setCurrentExercise] = useState("Push-ups");
  const [repCount, setRepCount] = useState(0);
  const [timer, setTimer] = useState(0);
  const [feedback, setFeedback] = useState("Position yourself in camera view");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [formQuality, setFormQuality] = useState(92);
  const [intensity, setIntensity] = useState(85);
  
  // Cycle tracking states
  const [cycleCount, setCycleCount] = useState(0);
  const [isOnBreak, setIsOnBreak] = useState(false);
  const [breakTimer, setBreakTimer] = useState(30);
  const [showBreakModal, setShowBreakModal] = useState(false);
  
  const lastRepCount = useRef(0);
  const breakIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const { toast } = useToast();

  // Get analysis-based exercises from localStorage or user data
  const getAnalysisExercises = () => {
    const workoutPlan = localStorage.getItem('workoutPlan');
    if (workoutPlan) {
      const plan = JSON.parse(workoutPlan);
      return plan.exercises.map((ex: any) => ex.name);
    }
    return ["Push-ups", "Squats", "Jumping Jacks"];
  };

  // Custom exercise options
  const customExercises = [
    "Squat", "Push-up", "Forward Lunge", "Jumping Jack", "Plank", 
    "Mountain Climber", "High Knees", "Burpee", "Jump Squat", "Side Lunge"
  ];

  // Calculate cycle information
  const currentCycles = calculateCycles(repCount, currentExercise);
  const repsInCurrentCycle = getRepsInCurrentCycle(repCount, currentExercise);
  const repsToNextCycle = getRepsToNextCycle(repCount, currentExercise);
  const exerciseConfig = getExerciseConfig(currentExercise);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isDetecting && sessionId && !isOnBreak) {
      interval = setInterval(() => {
        setTimer(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isDetecting, sessionId, isOnBreak]);

  // Handle break timer
  useEffect(() => {
    if (isOnBreak && breakTimer > 0) {
      breakIntervalRef.current = setInterval(() => {
        setBreakTimer(prev => {
          if (prev <= 1) {
            // Break is over
            setIsOnBreak(false);
            setShowBreakModal(false);
            setBreakTimer(30);
            if (breakIntervalRef.current) {
              clearInterval(breakIntervalRef.current);
              breakIntervalRef.current = null;
            }
            toast({
              title: "Break Complete!",
              description: "Time to continue your workout! 💪",
            });
            return 30;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => {
      if (breakIntervalRef.current) {
        clearInterval(breakIntervalRef.current);
        breakIntervalRef.current = null;
      }
    };
  }, [isOnBreak, breakTimer, toast]);

  // Update cycle count when rep count changes
  useEffect(() => {
    const newCycleCount = calculateCycles(repCount, currentExercise);
    if (newCycleCount > cycleCount) {
      setCycleCount(newCycleCount);
      
      // Check if a cycle was just completed
      if (isCycleComplete(repCount, currentExercise)) {
        setIsOnBreak(true);
        setShowBreakModal(true);
        setBreakTimer(30);
        
        toast({
          title: "🎉 Cycle Complete!",
          description: `Great job! Take a 30-second break before continuing.`,
        });
      }
    }
  }, [repCount, currentExercise, cycleCount]);

  const handleRepDetected = async (keypoints: any[], newRepCount: number) => {
    if (!sessionId || isOnBreak) return; // Don't process reps during break
    
    // Only process if this is actually a new rep (increased count)
    if (newRepCount <= lastRepCount.current) return;
    
    console.log(`Rep detected! Count: ${newRepCount}, Previous: ${lastRepCount.current}`);
    lastRepCount.current = newRepCount;
    setRepCount(newRepCount);
    setLoading(true);
    
    try {
      // Get pose feedback from backend
      const pose = await poseFeedbackAPI.getFeedback({
        pose_type: currentExercise.toLowerCase(),
        keypoints: keypoints,
        user_id: user?.username || "testuser"
      });
      
      setFeedback(pose.tips[0]);
      setFormQuality(Math.round(pose.score * 100));
      
      // Update workout session in backend
      if (sessionId) {
        await workoutAPI.update(sessionId, newRepCount, pose.score, pose.tips[0]);
      }
      
      // Update intensity based on rep count and time
      const newIntensity = Math.min(100, Math.max(50, 85 + (newRepCount * 2)));
      setIntensity(newIntensity);
      
      // Generate notification for significant progress (every 5 reps)
      if (newRepCount % 5 === 0 && newRepCount > 0) {
        if (typeof window !== 'undefined' && (window as any).generateWorkoutNotification) {
          (window as any).generateWorkoutNotification({
            reps: newRepCount,
            exercise: currentExercise,
            accuracy: Math.round(pose.score * 100),
            sessionId: sessionId
          });
        }
      }
      
    } catch (err) {
      console.error('Error getting feedback:', err);
      setFeedback("Error getting feedback");
      toast({
        title: "Error",
        description: "Failed to get pose feedback",
        variant: "destructive"
      });
    }
    setLoading(false);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const skipBreak = () => {
    setIsOnBreak(false);
    setShowBreakModal(false);
    setBreakTimer(30);
    if (breakIntervalRef.current) {
      clearInterval(breakIntervalRef.current);
      breakIntervalRef.current = null;
    }
    toast({
      title: "Break Skipped",
      description: "Continuing with your workout!",
    });
  };

  const toggleDetection = async () => {
    if (!isDetecting) {
      // Start workout session in backend
      setLoading(true);
      try {
        const res = await workoutAPI.start(currentExercise.toLowerCase());
        setSessionId(res.session_id);
        setRepCount(0);
        setCycleCount(0);
        lastRepCount.current = 0; // Reset the last rep count reference
        setTimer(0);
        setFeedback("Starting workout detection...");
        setFormQuality(92);
        setIntensity(85);
        setIsOnBreak(false);
        setShowBreakModal(false);
        setBreakTimer(30);
        toast({
          title: "Workout Started!",
          description: `Started ${currentExercise} session`,
        });
      } catch (err) {
        console.error('Error starting workout:', err);
        setFeedback("Failed to start workout session");
        toast({
          title: "Error",
          description: "Failed to start workout session",
          variant: "destructive"
        });
      }
      setLoading(false);
    } else {
      // End workout session and calculate points
      setLoading(true);
      try {
        if (repCount > 0) {
          console.log(`Calculating points for: ${currentExercise.toLowerCase()}, reps: ${repCount}`);
          const pointsResult = await pointsAPI.calculatePoints(currentExercise.toLowerCase(), repCount);
          console.log('Points result:', pointsResult);
          
          if (pointsResult.points_earned > 0) {
            toast({
              title: "🎉 Workout Complete!",
              description: `Earned ${pointsResult.points_earned} points! (${pointsResult.cycles_completed} cycles)`,
            });
          } else {
            toast({
              title: "Workout Complete!",
              description: `Completed ${repCount} reps. Complete a full cycle to earn points!`,
            });
          }
        }
      } catch (err) {
        console.error('Error calculating points:', err);
        toast({
          title: "Workout Complete!",
          description: `Completed ${repCount} reps`,
        });
      }
      setLoading(false);
      setFeedback("Workout completed");
    }
    setIsDetecting(!isDetecting);
  };

  const resetWorkout = () => {
    setIsDetecting(false);
    setRepCount(0);
    setCycleCount(0);
    lastRepCount.current = 0; // Reset the last rep count reference
    setTimer(0);
    setFeedback("Position yourself in camera view");
    setSessionId(null);
    setFormQuality(92);
    setIntensity(85);
    setIsOnBreak(false);
    setShowBreakModal(false);
    setBreakTimer(30);
    if (breakIntervalRef.current) {
      clearInterval(breakIntervalRef.current);
      breakIntervalRef.current = null;
    }
  };

  // Add handleFinish function
  const handleFinish = async () => {
    if (repCount < exerciseConfig.reps_per_cycle) {
      toast({
        title: "Not enough reps!",
        description: `Complete at least 1 cycle (${exerciseConfig.reps_per_cycle} reps) to earn points.`,
        variant: "destructive"
      });
      return;
    }
    setLoading(true);
    try {
      const pointsResult = await pointsAPI.calculatePoints(currentExercise.toLowerCase(), repCount);
      if (pointsResult.points_earned > 0) {
        toast({
          title: "🎉 Workout Finished!",
          description: `Earned ${pointsResult.points_earned} points! (${pointsResult.cycles_completed} cycles)`
        });
      } else {
        toast({
          title: "Workout Finished!",
          description: `Completed ${repCount} reps. Complete a full cycle to earn points!`
        });
      }
      // Notify other components to refresh points
      window.dispatchEvent(new Event('pointsUpdated'));
    } catch (err) {
      console.error('Error finishing workout:', err);
      toast({
        title: "Error",
        description: "Failed to update points",
        variant: "destructive"
      });
    }
    setLoading(false);
    setIsDetecting(false);
    setFeedback("Workout finished");
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
          AI Workout Detection
        </h1>
        <p className="text-muted-foreground">Real-time pose analysis and feedback</p>
      </div>

      {/* Exercise Selection */}
      <Card className="bg-gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-primary" />
            <span>Exercise Selection</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Exercise Mode Toggle */}
          <div className="flex flex-wrap gap-2">
            <Button
              variant={exerciseMode === "analysis" ? "hero" : "outline"}
              onClick={() => setExerciseMode("analysis")}
              className="flex-1 min-w-fit"
              disabled={isDetecting}
            >
              Use Analysis Plan
            </Button>
            <Button
              variant={exerciseMode === "custom" ? "hero" : "outline"}
              onClick={() => setExerciseMode("custom")}
              className="flex-1 min-w-fit"
              disabled={isDetecting}
            >
              Custom Selection
            </Button>
          </div>

          {/* Exercise Selector */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-muted-foreground">
              {exerciseMode === "analysis" ? "Recommended Exercises:" : "Choose Exercise:"}
            </label>
            {exerciseMode === "analysis" ? (
              <Select value={currentExercise} onValueChange={setCurrentExercise} disabled={isDetecting}>
                <SelectTrigger>
                  <SelectValue placeholder="Select exercise from your plan" />
                </SelectTrigger>
                <SelectContent>
                  {getAnalysisExercises().map((exercise) => (
                    <SelectItem key={exercise} value={exercise}>
                      {exercise}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : (
              <Select value={currentExercise} onValueChange={setCurrentExercise} disabled={isDetecting}>
                <SelectTrigger>
                  <SelectValue placeholder="Select custom exercise" />
                </SelectTrigger>
                <SelectContent>
                  {customExercises.map((exercise) => (
                    <SelectItem key={exercise} value={exercise}>
                      {exercise}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Webcam Feed */}
      <Card className="bg-gradient-dark border-border/50 overflow-hidden">
        <CardContent className="p-0">
          <div className="relative bg-black/20 aspect-video flex items-center justify-center">
            <div className="absolute inset-4 border-2 border-dashed border-primary/30 rounded-lg flex items-center justify-center">
              <PoseDetector
                isDetecting={isDetecting}
                exercise={currentExercise}
                onRepDetected={handleRepDetected}
              />
            </div>
            {isDetecting ? (
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <div className="space-y-4 text-center">
                  <div className="relative">
                    <div className="w-32 h-40 bg-gradient-primary/20 rounded-lg mx-auto animate-pulse" />
                    <div className="absolute top-2 left-2 w-4 h-4 bg-success rounded-full animate-ping" />
                    <div className="absolute top-2 right-2 w-4 h-4 bg-secondary rounded-full animate-ping" />
                    <div className="absolute bottom-2 left-2 w-4 h-4 bg-accent rounded-full animate-ping" />
                    <div className="absolute bottom-2 right-2 w-4 h-4 bg-energy rounded-full animate-ping" />
                  </div>
                  <p className="text-sm text-muted-foreground">Pose landmarks detected</p>
                </div>
              </div>
            ) : (
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <Zap className="w-16 h-16 text-muted-foreground mx-auto" />
                <p className="text-muted-foreground">Camera feed will appear here</p>
              </div>
            )}
            
            {/* Status Overlay */}
            <div className="absolute top-4 left-4 space-y-2">
              <Badge variant={isDetecting ? "default" : "secondary"} className="bg-black/50 backdrop-blur-sm">
                {isDetecting ? "🔴 LIVE" : "⏸️ PAUSED"}
              </Badge>
              <Badge variant="outline" className="bg-black/50 backdrop-blur-sm border-primary/30">
                {currentExercise}
              </Badge>
              {isOnBreak && (
                <Badge variant="destructive" className="bg-orange-500/80 backdrop-blur-sm">
                  ☕ ON BREAK
                </Badge>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats and Controls */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-card border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Rep Count</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-secondary">{repCount}</div>
            <div className="text-sm text-muted-foreground mt-1">
              {repsInCurrentCycle}/{exerciseConfig.reps_per_cycle} in current cycle
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-card border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground flex items-center space-x-2">
              <CheckCircle className="w-4 h-4" />
              <span>Cycles</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-success">{cycleCount}</div>
            <div className="text-sm text-muted-foreground mt-1">
              {repsToNextCycle} reps to next cycle
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-card border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground flex items-center space-x-2">
              <Timer className="w-4 h-4" />
              <span>Duration</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-primary">{formatTime(timer)}</div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-card border-border/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground flex items-center space-x-2">
              <Heart className="w-4 h-4" />
              <span>Intensity</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-accent">{intensity}%</div>
          </CardContent>
        </Card>
      </div>

      {/* Feedback Section */}
      <Card className="bg-gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-primary" />
            <span>Real-time Feedback</span>
            {loading && <Loader2 className="w-4 h-4 animate-spin" />}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="p-4 bg-primary/10 rounded-lg text-center">
            <p className="text-lg font-medium">{feedback}</p>
          </div>
          
          {/* Cycle Progress */}
          <div className="mt-4 space-y-4">
            <div>
              <div className="flex justify-between text-sm text-muted-foreground mb-2">
                <span>Current Cycle Progress</span>
                <span>{repsInCurrentCycle}/{exerciseConfig.reps_per_cycle}</span>
              </div>
              <Progress 
                value={(repsInCurrentCycle / exerciseConfig.reps_per_cycle) * 100} 
                className="h-3"
              />
            </div>
            
            <div>
              <div className="flex justify-between text-sm text-muted-foreground mb-2">
                <span>Form Quality</span>
                <span>{formQuality}%</span>
              </div>
              <Progress value={formQuality} className="h-2" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Controls */}
      <div className="flex flex-wrap justify-center gap-4">
        <Button
          variant={isDetecting ? "destructive" : "hero"}
          size="lg"
          onClick={toggleDetection}
          className="min-w-32"
          disabled={loading}
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              {isDetecting ? "Pausing..." : "Starting..."}
            </>
          ) : (
            isDetecting ? "Pause" : "Start Workout"
          )}
        </Button>
        <Button
          variant="outline"
          size="lg"
          onClick={resetWorkout}
          disabled={loading}
        >
          Reset
        </Button>
        {/* Finish Button */}
        <Button
          variant="success"
          size="lg"
          onClick={handleFinish}
          disabled={loading || repCount < exerciseConfig.reps_per_cycle}
        >
          Finish
        </Button>
        <Button
          variant="ghost"
          size="icon-lg"
          disabled={loading}
        >
          <Settings className="w-6 h-6" />
        </Button>
      </div>

      {/* Break Modal */}
      {showBreakModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <Card className="bg-gradient-card border-border/50 max-w-md w-full mx-4">
            <CardHeader className="text-center">
              <CardTitle className="flex items-center justify-center space-x-2 text-2xl">
                <Coffee className="w-8 h-8 text-primary" />
                <span>Take a Break!</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="text-center space-y-6">
              <div className="space-y-2">
                <p className="text-lg font-medium">Great job completing {cycleCount} cycle{cycleCount !== 1 ? 's' : ''}!</p>
                <p className="text-muted-foreground">Take a 30-second break to recover.</p>
              </div>
              
              <div className="space-y-2">
                <div className="text-6xl font-bold text-primary">{breakTimer}</div>
                <p className="text-sm text-muted-foreground">seconds remaining</p>
              </div>
              
              <div className="flex flex-col space-y-2">
                <Button
                  variant="outline"
                  onClick={skipBreak}
                  className="w-full"
                >
                  <Play className="w-4 h-4 mr-2" />
                  Skip Break
                </Button>
                <p className="text-xs text-muted-foreground">
                  Your workout is paused during this break
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};