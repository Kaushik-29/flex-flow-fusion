import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dumbbell, Users, Settings, Zap, LogOut, User, ChevronDown } from "lucide-react";
import { NotificationBell } from "@/components/notifications/NotificationBell";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

interface NavbarProps {
  currentView: string;
  onViewChange: (view: string) => void;
  user?: any;
  onLogout?: () => void;
}

export const Navbar = ({ currentView, onViewChange, user, onLogout }: NavbarProps) => {
  const [isOpen, setIsOpen] = useState(false);

  const navItems = [
    { id: "home", label: "Home", icon: Dumbbell },
    { id: "analysis", label: "Analysis", icon: Settings },
    { id: "leaderboard", label: "Leaderboard", icon: Users },
    { id: "workout", label: "Workout", icon: Zap },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  const handleLogout = () => {
    if (onLogout) {
      onLogout();
    }
  };

  const getUserInitials = (name?: string) => {
    if (!name) return "U";
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background border-b border-border shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-primary rounded-lg flex items-center justify-center">
              <Dumbbell className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              FLEX-IT-OUT
            </span>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              return (
                <Button
                  key={item.id}
                  variant={isActive ? "hero" : "ghost"}
                  size="sm"
                  onClick={() => onViewChange(item.id)}
                  className="flex items-center space-x-2"
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </Button>
              );
            })}
            <NotificationBell user={user} />
            
            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center space-x-2">
                  <Avatar className="w-8 h-8">
                    <AvatarImage src={user?.avatar} alt={user?.name} />
                    <AvatarFallback className="bg-primary text-primary-foreground text-sm font-medium">
                      {getUserInitials(user?.name)}
                    </AvatarFallback>
                  </Avatar>
                  <span className="hidden lg:block text-sm font-medium">
                    {user?.name || user?.username || "User"}
                  </span>
                  <ChevronDown className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">
                      {user?.name || user?.username}
                    </p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {user?.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => onViewChange("settings")}>
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-destructive">
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Logout</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <Button
              variant="ghost"
              size="icon-sm"
              onClick={() => setIsOpen(!isOpen)}
            >
              <div className="w-5 h-5 flex flex-col justify-center items-center">
                <div className={`w-4 h-0.5 bg-foreground transition-all ${isOpen ? 'rotate-45 translate-y-0.5' : ''}`} />
                <div className={`w-4 h-0.5 bg-foreground mt-1 transition-all ${isOpen ? '-rotate-45 -translate-y-0.5' : ''}`} />
              </div>
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isOpen && (
          <div className="md:hidden py-4 animate-slide-down">
            <div className="flex flex-col space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentView === item.id;
                return (
                  <Button
                    key={item.id}
                    variant={isActive ? "hero" : "ghost"}
                    size="sm"
                    onClick={() => {
                      onViewChange(item.id);
                      setIsOpen(false);
                    }}
                    className="flex items-center justify-start space-x-3 w-full"
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </Button>
                );
              })}
              
              {/* Mobile Logout */}
              <div className="pt-2 border-t border-border">
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => {
                    handleLogout();
                    setIsOpen(false);
                  }}
                  className="flex items-center justify-start space-x-3 w-full"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout</span>
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};