import { useState, useEffect } from "react";
import { Navbar } from "./layout/Navbar";
import { HeroSection } from "./hero/HeroSection";
import { AuthTabs } from "./auth/AuthTabs";
import { Dashboard } from "./dashboard/Dashboard";
import { WorkoutInterface } from "./workout/WorkoutInterface";
import { Leaderboard } from "./leaderboard/Leaderboard";
import { Settings } from "./settings/Settings";
import { Analysis } from "@/pages/Analysis";
import { authAPI } from "@/lib/api";

export const FlexItOutApp = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentView, setCurrentView] = useState("home");
  const [user, setUser] = useState<any>(null);

  const fetchUser = async () => {
    const token = localStorage.getItem("authToken");
    const storedUser = localStorage.getItem("currentUser");
    
    console.log('FlexItOutApp: Checking authentication state');
    console.log('FlexItOutApp: Token exists:', !!token);
    console.log('FlexItOutApp: Stored user exists:', !!storedUser);
    
    if (token) {
      try {
        // Try to get fresh user data from API
        console.log('FlexItOutApp: Attempting to fetch user data from API');
        const userData = await authAPI.getMe();
        console.log('FlexItOutApp: User data fetched successfully:', userData);
        setUser(userData);
        setIsAuthenticated(true);
        // Update stored user data
        localStorage.setItem("currentUser", JSON.stringify(userData));
      } catch (err) {
        console.error("Error fetching user info:", err);
        
        // If API call fails, try to use stored user data
        if (storedUser) {
          try {
            const parsedUser = JSON.parse(storedUser);
            console.log('FlexItOutApp: Using stored user data:', parsedUser);
            setUser(parsedUser);
            setIsAuthenticated(true);
            // Don't clear the token immediately - it might still be valid
            // Only clear if we get a specific 401 error
          } catch (parseErr) {
            console.error("Error parsing stored user data:", parseErr);
            setUser(null);
            setIsAuthenticated(false);
            localStorage.removeItem("authToken");
            localStorage.removeItem("currentUser");
          }
        } else {
          // If no stored user data and API fails, we might still have a valid token
          // but no user data. Let's keep the token and try again later
          console.log('FlexItOutApp: No stored user data, but keeping token for retry');
          setUser(null);
          setIsAuthenticated(false);
        }
      }
    } else if (storedUser) {
      // If no token but stored user data exists, clear it
      console.log('FlexItOutApp: No token but stored user exists, clearing stored data');
      localStorage.removeItem("currentUser");
      setUser(null);
      setIsAuthenticated(false);
    } else {
      console.log('FlexItOutApp: No token and no stored user data');
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const handleAuthSuccess = () => {
    setIsAuthenticated(true);
    setCurrentView("home");
    fetchUser();
  };

  const handleLogout = () => {
    // Clear user data and auth state
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem("authToken");
    localStorage.removeItem("currentUser");
    
    // Redirect to home page
    setCurrentView("home");
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const handleGetStarted = () => {
    setCurrentView("auth");
  };

  const renderContent = () => {
    if (!isAuthenticated) {
      if (currentView === "auth") {
        return <AuthTabs onAuthSuccess={handleAuthSuccess} />;
      }
      return <HeroSection onGetStarted={handleGetStarted} />;
    }

    switch (currentView) {
      case "home":
        return <Dashboard user={user} onViewChange={setCurrentView} />;
      case "analysis":
        return <Analysis onStartWorkout={() => setCurrentView("workout")} />;
      case "workout":
        return <WorkoutInterface user={user} />;
      case "leaderboard":
        return <Leaderboard />;
      case "settings":
        return <Settings user={user} onLogout={handleLogout} />;
      default:
        return <Dashboard user={user} onViewChange={setCurrentView} />;
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {isAuthenticated && (
        <Navbar currentView={currentView} onViewChange={setCurrentView} user={user} onLogout={handleLogout} />
      )}
      
      <main className={isAuthenticated ? "pt-16" : ""}>
        <div className={isAuthenticated ? "container mx-auto px-4 py-8" : ""}>
          {renderContent()}
        </div>
      </main>
    </div>
  );
};