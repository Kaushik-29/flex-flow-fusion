import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Settings as SettingsIcon, Bell, Zap, Users, Heart, LogOut, AlertTriangle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { FriendRequests } from "@/components/friends/FriendRequests";

interface SettingsProps {
  user?: {
    name?: string;
    username?: string;
    email?: string;
  };
  onLogout?: () => void;
}

export const Settings = ({ user, onLogout }: SettingsProps) => {
  const { toast } = useToast();
  const [notifications, setNotifications] = useState(true);
  const [sound, setSound] = useState(true);
  const [workoutReminders, setWorkoutReminders] = useState(true);
  const [leaderboardUpdates, setLeaderboardUpdates] = useState(true);

  const handleSave = () => {
    toast({
      title: "Settings saved! ✅",
      description: "Your preferences have been updated successfully.",
    });
  };

  const handlePasswordChange = () => {
    toast({
      title: "Password updated! 🔒",
      description: "Your password has been changed successfully.",
    });
  };

  const handleLogout = () => {
    // Clear auth token from localStorage
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    
    // Show logout confirmation
    toast({
      title: "Logged out successfully! 👋",
      description: "You have been logged out of your account.",
    });
    
    // Call the onLogout callback if provided
    if (onLogout) {
      onLogout();
    } else {
      // Default behavior: redirect to home page
      window.location.href = '/';
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold bg-gradient-accent bg-clip-text text-transparent">
          Settings ⚙️
        </h1>
        <p className="text-muted-foreground">Customize your FLEX-IT-OUT experience</p>
      </div>

      {/* Profile Settings */}
      <Card className="bg-gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="w-5 h-5 text-primary" />
            <span>Profile Settings</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="display-name">Display Name</Label>
              <Input
                id="display-name"
                defaultValue={user?.name || ""}
                className="bg-input/50 border-border/50 focus:border-primary"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                defaultValue={user?.username || ""}
                className="bg-input/50 border-border/50 focus:border-primary"
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              defaultValue={user?.email || ""}
              className="bg-input/50 border-border/50 focus:border-primary"
            />
          </div>
          <Button variant="secondary" onClick={handleSave}>
            Update Profile
          </Button>
        </CardContent>
      </Card>

      {/* Friend Requests */}
      <Card className="bg-gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="w-5 h-5 text-accent" />
            <span>Friend Requests</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <FriendRequests />
        </CardContent>
      </Card>

      {/* Password Settings */}
      <Card className="bg-gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Heart className="w-5 h-5 text-destructive" />
            <span>Security</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="current-password">Current Password</Label>
            <Input
              id="current-password"
              type="password"
              placeholder="Enter current password"
              className="bg-input/50 border-border/50 focus:border-primary"
            />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="new-password">New Password</Label>
              <Input
                id="new-password"
                type="password"
                placeholder="Enter new password"
                className="bg-input/50 border-border/50 focus:border-primary"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirm-password">Confirm New Password</Label>
              <Input
                id="confirm-password"
                type="password"
                placeholder="Confirm new password"
                className="bg-input/50 border-border/50 focus:border-primary"
              />
            </div>
          </div>
          <Button variant="destructive" onClick={handlePasswordChange}>
            Change Password
          </Button>
        </CardContent>
      </Card>

      {/* Notification Settings */}
      <Card className="bg-gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Bell className="w-5 h-5 text-secondary" />
            <span>Notifications</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="text-base font-medium">Push Notifications</Label>
              <p className="text-sm text-muted-foreground">
                Get notified about important updates and activities
              </p>
            </div>
            <Switch
              checked={notifications}
              onCheckedChange={setNotifications}
            />
          </div>
          
          <Separator />
          
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="text-base font-medium">Sound Effects</Label>
              <p className="text-sm text-muted-foreground">
                Play sounds for workout feedback and achievements
              </p>
            </div>
            <Switch
              checked={sound}
              onCheckedChange={setSound}
            />
          </div>
          
          <Separator />
          
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="text-base font-medium">Workout Reminders</Label>
              <p className="text-sm text-muted-foreground">
                Daily reminders to maintain your fitness streak
              </p>
            </div>
            <Switch
              checked={workoutReminders}
              onCheckedChange={setWorkoutReminders}
            />
          </div>
          
          <Separator />
          
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label className="text-base font-medium">Leaderboard Updates</Label>
              <p className="text-sm text-muted-foreground">
                Get notified when you climb ranks or friends beat your score
              </p>
            </div>
            <Switch
              checked={leaderboardUpdates}
              onCheckedChange={setLeaderboardUpdates}
            />
          </div>
        </CardContent>
      </Card>

      {/* App Preferences */}
      <Card className="bg-gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-energy" />
            <span>App Preferences</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="language">Language</Label>
              <Select defaultValue="en">
                <SelectTrigger className="bg-input/50 border-border/50 focus:border-primary">
                  <SelectValue placeholder="Select language" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="es">Español</SelectItem>
                  <SelectItem value="fr">Français</SelectItem>
                  <SelectItem value="de">Deutsch</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="units">Units</Label>
              <Select defaultValue="metric">
                <SelectTrigger className="bg-input/50 border-border/50 focus:border-primary">
                  <SelectValue placeholder="Select units" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="metric">Metric (kg, cm)</SelectItem>
                  <SelectItem value="imperial">Imperial (lbs, ft)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <Button variant="secondary" onClick={handleSave}>
            Save Preferences
          </Button>
        </CardContent>
      </Card>

      {/* Social Connections */}
      <Card className="bg-gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Users className="w-5 h-5 text-accent" />
            <span>Social Connections</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-primary/5 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                f
              </div>
              <div>
                <p className="font-medium">Facebook</p>
                <p className="text-sm text-muted-foreground">Not connected</p>
              </div>
            </div>
            <Button variant="outline" size="sm">
              Connect
            </Button>
          </div>
          
          <div className="flex items-center justify-between p-4 bg-success/5 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                G
              </div>
              <div>
                <p className="font-medium">Google</p>
                <p className="text-sm text-success">Connected as alex.johnson@gmail.com</p>
              </div>
            </div>
            <Button variant="destructive" size="sm">
              Disconnect
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Account Actions */}
      <Card className="bg-gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-destructive" />
            <span>Account Actions</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="p-4 bg-destructive/5 rounded-lg border border-destructive/20">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="font-medium text-destructive">Logout</p>
                <p className="text-sm text-muted-foreground">
                  Sign out of your account and return to the login page
                </p>
              </div>
              <Button 
                variant="destructive" 
                onClick={handleLogout}
                className="flex items-center space-x-2"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </Button>
            </div>
          </div>
          
          <Separator />
          
          <div className="p-4 bg-amber-500/5 rounded-lg border border-amber-500/20">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="font-medium text-amber-600">Delete Account</p>
                <p className="text-sm text-muted-foreground">
                  Permanently delete your account and all associated data
                </p>
              </div>
              <Button 
                variant="outline" 
                className="border-amber-500/50 text-amber-600 hover:bg-amber-500/10"
              >
                Delete Account
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};