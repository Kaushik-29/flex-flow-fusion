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
import { auth, isConfigured } from "@/lib/firebaseClient";
import { onAuthStateChanged, signOut } from "firebase/auth";

export const FlexItOutApp = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentView, setCurrentView] = useState("home");
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    if (!isConfigured) {
      // Local/offline mode: check localStorage for authToken
      const localToken = localStorage.getItem("authToken");
      if (localToken) {
        authAPI.getMe()
          .then((userData) => {
            setUser(userData);
            setIsAuthenticated(true);
            localStorage.setItem("currentUser", JSON.stringify(userData));
          })
          .catch((err) => {
            console.error("Local token verification failed:", err);
            setUser(null);
            setIsAuthenticated(false);
            localStorage.removeItem("authToken");
            localStorage.removeItem("currentUser");
          });
      }
      return;
    }

    // Firebase mode: subscribe to auth state changes
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      console.log("Firebase Auth State Changed:", !!firebaseUser);
      if (firebaseUser) {
        try {
          const idToken = await firebaseUser.getIdToken();
          localStorage.setItem("authToken", idToken);
          
          const userData = await authAPI.getMe();
          setUser(userData);
          setIsAuthenticated(true);
          localStorage.setItem("currentUser", JSON.stringify(userData));
        } catch (err) {
          console.error("Auth change fetch error:", err);
          const fallbackUser = {
            name: firebaseUser.displayName || firebaseUser.email?.split("@")[0] || "User",
            username: firebaseUser.email?.split("@")[0] || "user",
            email: firebaseUser.email || ""
          };
          setUser(fallbackUser);
          setIsAuthenticated(true);
        }
      } else {
        setUser(null);
        setIsAuthenticated(false);
        localStorage.removeItem("authToken");
        localStorage.removeItem("currentUser");
      }
    });

    return () => unsubscribe();
  }, []);

  const handleAuthSuccess = () => {
    setIsAuthenticated(true);
    setCurrentView("home");
  };

  const handleLogout = async () => {
    if (isConfigured) {
      try {
        await signOut(auth);
      } catch (err) {
        console.error("Firebase signOut failed:", err);
      }
    }
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem("authToken");
    localStorage.removeItem("currentUser");
    setCurrentView("home");
  };

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