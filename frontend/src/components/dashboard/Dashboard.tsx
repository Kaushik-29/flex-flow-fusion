import { UserProfile } from "./UserProfile";
import { QuickActions } from "./QuickActions";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Bell, Heart, Zap, Dumbbell, Calculator, Trophy } from "lucide-react";
import { useEffect, useState } from "react";
import { pointsAPI } from "@/lib/api";

interface DashboardProps {
  onViewChange: (view: string) => void;
  user?: any;
}

export const Dashboard = ({ onViewChange, user }: DashboardProps) => {
  const [hasWorkoutPlan, setHasWorkoutPlan] = useState(false);
  const [userPoints, setUserPoints] = useState(0);

  useEffect(() => {
    const workoutPlan = localStorage.getItem('workoutPlan');
    setHasWorkoutPlan(!!workoutPlan);
    
    // Fetch user points
    const fetchUserPoints = async () => {
      try {
        const response = await pointsAPI.getUserPoints();
        setUserPoints(response.total_points || 0);
      } catch (error) {
        console.error('Error fetching user points:', error);
      }
    };
    
    fetchUserPoints();
  }, []);

  const motivationalQuotes = [
    "Push harder today, celebrate tomorrow! 💪",
    "Your only competition is who you were yesterday.",
    "Strength grows in the moments when you think you can't go on.",
    "The body achieves what the mind believes! 🔥"
  ];

  const todayQuote = motivationalQuotes[Math.floor(Math.random() * motivationalQuotes.length)];

  const stats = [
    { label: "Total Points", value: userPoints.toString(), icon: Trophy, color: "text-primary" },
    { label: "Workouts This Week", value: "12", icon: Dumbbell, color: "text-secondary" },
    { label: "Streak Days", value: "28", icon: Heart, color: "text-accent" }
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Welcome Section */}
      <div className="text-center space-y-2">
        <h1 className="text-4xl font-bold bg-gradient-primary bg-clip-text text-transparent">
          Welcome back, {user?.name || user?.username || "User"}! 👋
        </h1>
        <p className="text-lg text-muted-foreground italic">"{todayQuote}"</p>
      </div>

      {/* User Profile */}
      {user && <UserProfile user={user} />}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label} className="bg-gradient-card border-border/50">
              <CardContent className="p-6 text-center">
                <Icon className={`w-8 h-8 mx-auto mb-2 ${stat.color}`} />
                <div className="text-3xl font-bold text-foreground">{stat.value}</div>
                <p className="text-sm text-muted-foreground">{stat.label}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Workout Plan Check */}
      {!hasWorkoutPlan && (
        <Card className="bg-gradient-card border-border/50 border-primary/20">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Calculator className="w-5 h-5 text-primary" />
              <span>Get Your Personalized Workout Plan</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              Complete a quick fitness analysis to get your personalized workout plan based on your goals and fitness level.
            </p>
            <Button 
              onClick={() => onViewChange("analysis")} 
              className="w-full" 
              variant="hero"
            >
              <Calculator className="w-4 h-4 mr-2" />
              Start Fitness Analysis
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-4">Quick Actions</h2>
        <QuickActions onActionClick={onViewChange} />
      </div>

      {/* Notifications Panel */}
      <Card className="bg-gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Bell className="w-5 h-5 text-primary" />
            <span>Recent Activity</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center space-x-3 p-3 bg-primary/10 rounded-lg">
              <div className="w-2 h-2 bg-success rounded-full animate-pulse" />
              <span className="text-sm">🏆 You climbed 5 ranks in the leaderboard!</span>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-secondary/10 rounded-lg">
              <div className="w-2 h-2 bg-secondary rounded-full" />
              <span className="text-sm">💪 New challenge available: "30-Day Push-up Challenge"</span>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-accent/10 rounded-lg">
              <div className="w-2 h-2 bg-accent rounded-full" />
              <span className="text-sm">🔥 Your workout streak reached 28 days!</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};