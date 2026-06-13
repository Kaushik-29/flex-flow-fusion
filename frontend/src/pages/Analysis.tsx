import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Calculator, Target, PlayIcon, Calendar, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { notificationsAPI } from "@/lib/api";

interface UserData {
  height: number;
  weight: number;
  age: number;
  gender: string;
}

interface WorkoutPlan {
  exercises: Array<{
    name: string;
    reps: number;
    sets: number;
    category: string;
  }>;
  category: 'Gain' | 'Maintain' | 'Lose';
  bmi: number;
}

interface DailyProgress {
  date: string;
  exercises: Array<{
    name: string;
    completed: number;
    target: number;
  }>;
  completionPercentage: number;
}

export const Analysis = ({ onStartWorkout }: { onStartWorkout: () => void }) => {
  const [userData, setUserData] = useState<UserData>({
    height: 0,
    weight: 0,
    age: 0,
    gender: ''
  });
  const [workoutPlan, setWorkoutPlan] = useState<WorkoutPlan | null>(null);
  const [dailyProgress, setDailyProgress] = useState<DailyProgress | null>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  // Load existing data on component mount
  useEffect(() => {
    const savedUserData = localStorage.getItem('userFitnessData');
    const savedWorkoutPlan = localStorage.getItem('workoutPlan');
    const savedDailyProgress = localStorage.getItem('dailyProgress');
    
    if (savedUserData) {
      setUserData(JSON.parse(savedUserData));
    }
    if (savedWorkoutPlan) {
      setWorkoutPlan(JSON.parse(savedWorkoutPlan));
    }
    if (savedDailyProgress) {
      setDailyProgress(JSON.parse(savedDailyProgress));
    }
  }, []);

  const calculateBMI = (weight: number, height: number) => {
    const heightInMeters = height / 100;
    return weight / (heightInMeters * heightInMeters);
  };

  const getFitnessCategory = (bmi: number, age: number): 'Gain' | 'Maintain' | 'Lose' => {
    if (bmi < 18.5) return 'Gain';
    if (bmi > 25) return 'Lose';
    return 'Maintain';
  };

  const generateWorkoutPlan = (category: string, userData: UserData): WorkoutPlan => {
    const bmi = calculateBMI(userData.weight, userData.height);
    
    const basePlans = {
      Gain: [
        { name: "Push-ups", reps: 15, sets: 3, category: "Strength" },
        { name: "Squats", reps: 20, sets: 3, category: "Strength" },
        { name: "Burpees", reps: 10, sets: 2, category: "Full Body" },
        { name: "Planks", reps: 45, sets: 3, category: "Core" },
      ],
      Maintain: [
        { name: "Push-ups", reps: 12, sets: 3, category: "Strength" },
        { name: "Jumping Jacks", reps: 30, sets: 2, category: "Cardio" },
        { name: "Lunges", reps: 15, sets: 3, category: "Legs" },
        { name: "Mountain Climbers", reps: 20, sets: 2, category: "Cardio" },
      ],
      Lose: [
        { name: "High Knees", reps: 30, sets: 3, category: "Cardio" },
        { name: "Jumping Jacks", reps: 40, sets: 3, category: "Cardio" },
        { name: "Burpees", reps: 12, sets: 3, category: "Full Body" },
        { name: "Russian Twists", reps: 25, sets: 3, category: "Core" },
      ]
    };

    return {
      exercises: basePlans[category as keyof typeof basePlans],
      category: category as 'Gain' | 'Maintain' | 'Lose',
      bmi
    };
  };

  const handleAnalyze = async () => {
    if (!userData.height || !userData.weight || !userData.age || !userData.gender) {
      toast({
        title: "Missing Information",
        description: "Please fill in all fields to get your analysis.",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const bmi = calculateBMI(userData.weight, userData.height);
      const category = getFitnessCategory(bmi, userData.age);
      const plan = generateWorkoutPlan(category, userData);
      
      setWorkoutPlan(plan);
      
      // Save to localStorage
      localStorage.setItem('userFitnessData', JSON.stringify(userData));
      localStorage.setItem('workoutPlan', JSON.stringify(plan));
      
      // Initialize today's progress
      const today = new Date().toISOString().split('T')[0];
      const todayProgress: DailyProgress = {
        date: today,
        exercises: plan.exercises.map(ex => ({
          name: ex.name,
          completed: 0,
          target: ex.reps * ex.sets
        })),
        completionPercentage: 0
      };
      
      setDailyProgress(todayProgress);
      localStorage.setItem('dailyProgress', JSON.stringify(todayProgress));

      // Generate notification for new workout plan
      try {
        await notificationsAPI.createNotification({
          type: 'workout_plan',
          title: "New Workout Plan Available!",
          message: `Your personalized ${category} workout plan is ready with ${plan.exercises.length} exercises.`,
          data: plan
        });
      } catch (error) {
        console.error('Error creating notification:', error);
      }

      toast({
        title: "Analysis Complete!",
        description: `Your fitness category: ${category}. Workout plan generated!`
      });
    } catch (error) {
      console.error('Error during analysis:', error);
      toast({
        title: "Error",
        description: "Failed to complete analysis. Please try again.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleStartWorkout = () => {
    if (workoutPlan) {
      localStorage.setItem('currentWorkout', JSON.stringify(workoutPlan));
      onStartWorkout();
    }
  };

  const getBMICategory = (bmi: number) => {
    if (bmi < 18.5) return { text: "Underweight", color: "text-blue-500" };
    if (bmi < 25) return { text: "Normal", color: "text-success" };
    if (bmi < 30) return { text: "Overweight", color: "text-energy" };
    return { text: "Obese", color: "text-destructive" };
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
          Fitness Analysis & Workout Tracker
        </h1>
        <p className="text-muted-foreground">Get your personalized workout plan</p>
      </div>

      {/* Input Form */}
      <Card className="bg-gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Calculator className="w-5 h-5 text-primary" />
            <span>Personal Information</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="height">Height (cm)</Label>
              <Input
                id="height"
                type="number"
                placeholder="170"
                value={userData.height || ''}
                onChange={(e) => setUserData(prev => ({ ...prev, height: parseInt(e.target.value) }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="weight">Weight (kg)</Label>
              <Input
                id="weight"
                type="number"
                placeholder="70"
                value={userData.weight || ''}
                onChange={(e) => setUserData(prev => ({ ...prev, weight: parseInt(e.target.value) }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="age">Age</Label>
              <Input
                id="age"
                type="number"
                placeholder="25"
                value={userData.age || ''}
                onChange={(e) => setUserData(prev => ({ ...prev, age: parseInt(e.target.value) }))}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="gender">Gender</Label>
              <Select value={userData.gender} onValueChange={(value) => setUserData(prev => ({ ...prev, gender: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Select gender" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="male">Male</SelectItem>
                  <SelectItem value="female">Female</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <Button onClick={handleAnalyze} className="w-full" size="lg" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Calculator className="w-4 h-4 mr-2" />
                Analyze My Fitness
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {workoutPlan && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="bg-gradient-card border-border/50">
              <CardHeader>
                <CardTitle className="text-lg">BMI Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center space-y-2">
                  <div className="text-4xl font-bold text-primary">
                    {workoutPlan.bmi.toFixed(1)}
                  </div>
                  <Badge className={getBMICategory(workoutPlan.bmi).color}>
                    {getBMICategory(workoutPlan.bmi).text}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-card border-border/50">
              <CardHeader>
                <CardTitle className="text-lg">Fitness Category</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center space-y-2">
                  <div className="text-4xl font-bold text-secondary">
                    {workoutPlan.category}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {workoutPlan.category === 'Gain' && 'Focus on muscle building'}
                    {workoutPlan.category === 'Maintain' && 'Keep your current fitness'}
                    {workoutPlan.category === 'Lose' && 'Focus on cardio and fat burning'}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card className="bg-gradient-card border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Target className="w-5 h-5 text-accent" />
                <span>Your Workout Plan</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-3">
                {workoutPlan.exercises.map((exercise, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-primary/5 rounded-lg">
                    <div>
                      <h4 className="font-semibold">{exercise.name}</h4>
                      <p className="text-sm text-muted-foreground">
                        {exercise.sets} sets × {exercise.reps} reps
                      </p>
                    </div>
                    <Badge variant="outline">{exercise.category}</Badge>
                  </div>
                ))}
              </div>
              <Button onClick={handleStartWorkout} className="w-full" size="lg" variant="hero">
                <PlayIcon className="w-4 h-4 mr-2" />
                Start Workout
              </Button>
            </CardContent>
          </Card>

          {dailyProgress && (
            <Card className="bg-gradient-card border-border/50">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Calendar className="w-5 h-5 text-energy" />
                  <span>Today's Progress</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Completion</span>
                    <span>{dailyProgress.completionPercentage}%</span>
                  </div>
                  <Progress value={dailyProgress.completionPercentage} className="h-2" />
                </div>
                <div className="space-y-2">
                  {dailyProgress.exercises.map((exercise, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <span className="text-sm">{exercise.name}</span>
                      <span className="text-sm text-muted-foreground">
                        {exercise.completed}/{exercise.target}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
};