import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dumbbell, Users, Zap, Timer } from "lucide-react";

interface QuickActionsProps {
  onActionClick: (action: string) => void;
}

export const QuickActions = ({ onActionClick }: QuickActionsProps) => {
  const actions = [
    {
      id: "workout",
      title: "Start Workout",
      description: "Begin AI-powered pose detection",
      icon: Dumbbell,
      variant: "hero" as const,
      gradient: "bg-gradient-primary"
    },
    {
      id: "challenge",
      title: "Join Challenge",
      description: "Compete with friends live",
      icon: Users,
      variant: "secondary" as const,
      gradient: "bg-gradient-secondary"
    },
    {
      id: "leaderboard",
      title: "Leaderboard",
      description: "Check your ranking",
      icon: Zap,
      variant: "accent" as const,
      gradient: "bg-gradient-accent"
    },
    {
      id: "tutorials",
      title: "Tutorials",
      description: "Learn new exercises",
      icon: Timer,
      variant: "energy" as const,
      gradient: "bg-energy"
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {actions.map((action, index) => {
        const Icon = action.icon;
        return (
          <Card 
            key={action.id} 
            className="bg-gradient-card border-border/50 hover:border-primary/30 transition-all duration-300 group cursor-pointer"
            style={{ animationDelay: `${index * 100}ms` }}
            onClick={() => onActionClick(action.id)}
          >
            <CardHeader className="pb-3">
              <div className={`w-12 h-12 ${action.gradient} rounded-xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform duration-300`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
              <CardTitle className="text-lg font-semibold">{action.title}</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <p className="text-sm text-muted-foreground mb-4">{action.description}</p>
              <Button 
                variant={action.variant} 
                size="sm" 
                className="w-full"
                onClick={(e) => {
                  e.stopPropagation();
                  onActionClick(action.id);
                }}
              >
                Get Started
              </Button>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};