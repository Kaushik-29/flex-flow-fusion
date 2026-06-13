import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, Zap } from "lucide-react";

interface UserProfileProps {
  user: {
    name?: string;
    username?: string;
    email?: string;
    avatar?: string;
    totalPoints?: number;
    rank?: number;
    level?: string;
  };
}

export const UserProfile = ({ user }: UserProfileProps) => {
  return (
    <Card className="bg-gradient-card border-border/50 overflow-hidden">
      <CardContent className="p-6">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Avatar className="w-16 h-16 ring-2 ring-primary/30">
              <AvatarImage src={user?.avatar || ""} alt={user?.name || user?.username || "User"} />
              <AvatarFallback className="bg-gradient-primary text-primary-foreground text-lg font-bold">
                {(user?.name || user?.username || "U").split(' ').map(n => n[0]).join('')}
              </AvatarFallback>
            </Avatar>
            <div className="absolute -top-1 -right-1 w-5 h-5 bg-success rounded-full border-2 border-background animate-pulse" />
          </div>
          
          <div className="flex-1">
            <h2 className="text-xl font-bold text-foreground">{user?.name || user?.username || "User"}</h2>
            <p className="text-muted-foreground">@{user?.username || user?.email || "user"}</p>
            <div className="flex items-center space-x-3 mt-2">
              <Badge variant="secondary" className="bg-primary/20 text-primary border-primary/30">
                <Zap className="w-3 h-3 mr-1" />
                {user?.level || "Member"}
              </Badge>
              <Badge variant="outline" className="border-secondary/30 text-secondary">
                <Users className="w-3 h-3 mr-1" />
                Rank #{user?.rank ?? "-"}
              </Badge>
            </div>
          </div>
          
          <div className="text-right">
            <div className="text-3xl font-bold bg-gradient-secondary bg-clip-text text-transparent">
              {user?.totalPoints?.toLocaleString?.() || 0}
            </div>
            <p className="text-xs text-muted-foreground">Total Points</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};