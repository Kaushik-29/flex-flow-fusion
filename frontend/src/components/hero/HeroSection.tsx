import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dumbbell, Zap, Users, Heart } from "lucide-react";
import heroImage from "@/assets/hero-image.jpg";

interface HeroSectionProps {
  onGetStarted: () => void;
}

export const HeroSection = ({ onGetStarted }: HeroSectionProps) => {
  const features = [
    { icon: Zap, title: "AI Pose Detection", desc: "Real-time workout analysis" },
    { icon: Users, title: "Live Challenges", desc: "Compete with friends" },
    { icon: Heart, title: "Instant Feedback", desc: "Perfect your form" },
    { icon: Dumbbell, title: "Gamified Fitness", desc: "Level up your workouts" }
  ];

  return (
    <div className="min-h-screen bg-gradient-dark relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-20 left-20 w-72 h-72 bg-primary/20 rounded-full blur-3xl animate-float" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-secondary/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-accent/20 rounded-full blur-3xl animate-bounce-slow" />
      </div>

      <div className="container mx-auto px-4 py-20 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center min-h-screen">
          {/* Left Content */}
          <div className="space-y-8 animate-slide-up">
            <div className="space-y-4">
              <Badge className="bg-gradient-primary text-primary-foreground px-4 py-2 text-sm font-semibold">
                🚀 AI-Powered Fitness Revolution
              </Badge>
              
              <h1 className="text-5xl lg:text-7xl font-black leading-tight">
                <span className="bg-gradient-primary bg-clip-text text-transparent">
                  FLEX
                </span>
                <span className="text-foreground">-IT-</span>
                <span className="bg-gradient-secondary bg-clip-text text-transparent">
                  OUT
                </span>
              </h1>
              
              <p className="text-xl lg:text-2xl text-muted-foreground leading-relaxed">
                Turn your workouts into an <span className="text-primary font-semibold">epic gaming experience</span> with 
                real-time AI pose detection, live challenges, and instant feedback that makes fitness fun!
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Button 
                variant="hero" 
                size="xl" 
                onClick={onGetStarted}
                className="animate-pulse-glow"
              >
                Start Your Journey 🚀
              </Button>
              <Button variant="outline" size="xl">
                Watch Demo 📽️
              </Button>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {features.map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <Card 
                    key={feature.title} 
                    className="bg-white/5 backdrop-blur-sm border-white/10 hover:bg-white/10 transition-all duration-300"
                    style={{ animationDelay: `${index * 150}ms` }}
                  >
                    <CardContent className="p-4 text-center">
                      <Icon className="w-8 h-8 mx-auto mb-2 text-primary" />
                      <h3 className="font-semibold text-sm text-foreground">{feature.title}</h3>
                      <p className="text-xs text-muted-foreground mt-1">{feature.desc}</p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </div>

          {/* Right Content - Hero Image */}
          <div className="relative animate-float">
            <div className="relative">
              <img 
                src={heroImage} 
                alt="FLEX-IT-OUT AI Fitness" 
                className="w-full h-auto rounded-3xl shadow-2xl border border-white/10"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-background/80 via-transparent to-transparent rounded-3xl" />
              
              {/* Floating Stats */}
              <div className="absolute top-6 right-6 bg-black/40 backdrop-blur-md rounded-2xl p-4 border border-white/20">
                <div className="text-center">
                  <div className="text-2xl font-bold text-secondary">15.2K+</div>
                  <p className="text-xs text-muted-foreground">Active Users</p>
                </div>
              </div>
              
              <div className="absolute bottom-6 left-6 bg-black/40 backdrop-blur-md rounded-2xl p-4 border border-white/20">
                <div className="text-center">
                  <div className="text-2xl font-bold text-accent">98%</div>
                  <p className="text-xs text-muted-foreground">Accuracy Rate</p>
                </div>
              </div>
            </div>

            {/* Floating Elements */}
            <div className="absolute -top-4 -left-4 w-16 h-16 bg-gradient-primary rounded-2xl flex items-center justify-center animate-bounce-slow">
              <Dumbbell className="w-8 h-8 text-primary-foreground" />
            </div>
            
            <div className="absolute -bottom-4 -right-4 w-16 h-16 bg-gradient-secondary rounded-2xl flex items-center justify-center animate-pulse">
              <Zap className="w-8 h-8 text-secondary-foreground" />
            </div>
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-20 space-y-6">
          <h2 className="text-3xl font-bold text-foreground">
            Ready to revolutionize your fitness journey?
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Join thousands of fitness enthusiasts who are already crushing their goals with AI-powered workouts!
          </p>
          <div className="flex justify-center space-x-8 text-sm text-muted-foreground">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-success rounded-full" />
              <span>Free to start</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-secondary rounded-full" />
              <span>No equipment needed</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-accent rounded-full" />
              <span>Works on any device</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};