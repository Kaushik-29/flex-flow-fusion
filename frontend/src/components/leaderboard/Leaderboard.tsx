import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Users, Zap, Timer, Bell, UserPlus, Search, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { leaderboardAPI, friendsAPI, pointsAPI } from "@/lib/api";

interface LeaderboardUser {
  rank: number;
  user_id: string;
  name: string;
  username: string;
  avatar: string;
  points: number;
  badge: string;
  avg_accuracy: number;
  total_workouts: number;
  isYou: boolean;
}

interface SearchUser {
  user_id: string;
  name: string;
  username: string;
  avatar: string;
  badge: string;
}

export const Leaderboard = () => {
  const [selectedPeriod, setSelectedPeriod] = useState("weekly");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchUser[]>([]);
  const [globalLeaderboard, setGlobalLeaderboard] = useState<LeaderboardUser[]>([]);
  const [friendsLeaderboard, setFriendsLeaderboard] = useState<LeaderboardUser[]>([]);
  const [pointsLeaderboard, setPointsLeaderboard] = useState<LeaderboardUser[]>([]);
  const [friendsPoints, setFriendsPoints] = useState<LeaderboardUser[]>([]);
  const [userPoints, setUserPoints] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const { toast } = useToast();

  // Get current user from localStorage or context
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');

  const fetchLeaderboard = async (period: string) => {
    setLoading(true);
    try {
      const response = await leaderboardAPI.getTop(period, 10);
      const leaderboardData = response.leaderboard.map((user: any) => ({
        ...user,
        isYou: user.username === currentUser.username
      }));
      setGlobalLeaderboard(leaderboardData);
      
      // For now, friends leaderboard is the same as global
      // In a real app, you'd have a separate endpoint for friends
      setFriendsLeaderboard(leaderboardData);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
      toast({
        title: "Error",
        description: "Failed to load leaderboard data",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchPointsLeaderboard = async () => {
    setLoading(true);
    try {
      const response = await pointsAPI.getPointsLeaderboard(50);
      const pointsData = response.leaderboard.map((user: any, index: number) => ({
        rank: index + 1,
        user_id: user.user_id,
        name: user.name,
        username: user.username,
        avatar: user.avatar || "",
        points: user.total_points,
        badge: getBadgeByRank(index + 1),
        avg_accuracy: 0,
        total_workouts: 0,
        isYou: user.username === currentUser.username
      }));
      setPointsLeaderboard(pointsData);
    } catch (error) {
      console.error('Error fetching points leaderboard:', error);
      toast({
        title: "Error",
        description: "Failed to load points leaderboard",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchFriendsPoints = async () => {
    setLoading(true);
    try {
      const response = await pointsAPI.getFriendsPoints();
      setUserPoints(response.current_user_points);
      
      const friendsData = response.friends_points.map((user: any, index: number) => ({
        rank: index + 1,
        user_id: user.user_id,
        name: user.name || user.user_id,
        username: user.user_id,
        avatar: "",
        points: user.total_points,
        badge: getBadgeByRank(index + 1),
        avg_accuracy: 0,
        total_workouts: 0,
        isYou: false
      }));
      setFriendsPoints(friendsData);
    } catch (error) {
      console.error('Error fetching friends points:', error);
      toast({
        title: "Error",
        description: "Failed to load friends points",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getBadgeByRank = (rank: number) => {
    if (rank === 1) return "🏆";
    if (rank === 2) return "🥈";
    if (rank === 3) return "🥉";
    if (rank <= 10) return "⚡";
    if (rank <= 50) return "💪";
    return "🔥";
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    if (query.trim().length < 2) {
      setSearchResults([]);
      return;
    }

    setSearchLoading(true);
    try {
      const response = await leaderboardAPI.searchUsers(query);
      const filteredResults = response.users.filter(
        (user: SearchUser) => user.username !== currentUser.username
      );
      setSearchResults(filteredResults.slice(0, 5));
    } catch (error) {
      console.error('Error searching users:', error);
      toast({
        title: "Error",
        description: "Failed to search users",
        variant: "destructive"
      });
    } finally {
      setSearchLoading(false);
    }
  };

  const sendFriendRequest = async (username: string) => {
    try {
      await friendsAPI.sendRequest(username);
      toast({
        title: "Friend Request Sent!",
        description: `Sent friend request to ${username}`
      });
    } catch (error) {
      console.error('Error sending friend request:', error);
      toast({
        title: "Error",
        description: "Failed to send friend request",
        variant: "destructive"
      });
    }
  };

  useEffect(() => {
    fetchLeaderboard(selectedPeriod);
    fetchPointsLeaderboard();
    fetchFriendsPoints();
  }, [selectedPeriod]);

  // Listen for pointsUpdated event to refresh data
  useEffect(() => {
    const handlePointsUpdated = () => {
      fetchLeaderboard(selectedPeriod);
      fetchPointsLeaderboard();
      fetchFriendsPoints();
    };
    window.addEventListener('pointsUpdated', handlePointsUpdated);
    return () => window.removeEventListener('pointsUpdated', handlePointsUpdated);
  }, [selectedPeriod]);

  const getRankColor = (rank: number) => {
    if (rank === 1) return "text-yellow-400";
    if (rank === 2) return "text-gray-300";
    if (rank === 3) return "text-orange-400";
    return "text-muted-foreground";
  };

  const getCardStyle = (isYou: boolean) => {
    return isYou 
      ? "bg-gradient-primary/10 border-primary/50 ring-1 ring-primary/30" 
      : "bg-gradient-card border-border/50";
  };

  const renderLeaderboard = (data: LeaderboardUser[], title: string) => (
    <Card className="bg-gradient-card border-border/50">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Zap className="w-5 h-5 text-secondary" />
          <span>{title}</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span className="ml-2">Loading leaderboard...</span>
          </div>
        ) : data.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No data available
          </div>
        ) : (
          data.map((user) => (
            <div
              key={user.user_id}
              className={`flex items-center space-x-4 p-4 rounded-xl transition-all duration-300 hover:scale-[1.02] ${getCardStyle(user.isYou)}`}
            >
              <div className={`text-2xl font-bold ${getRankColor(user.rank)} min-w-8`}>
                #{user.rank}
              </div>
              <div className="text-2xl">{user.badge}</div>
              <Avatar className="w-12 h-12">
                <AvatarImage src={user.avatar} alt={user.name} />
                <AvatarFallback className="bg-gradient-primary text-primary-foreground text-sm font-bold">
                  {user.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1">
                <h3 className={`font-semibold ${user.isYou ? 'text-primary' : 'text-foreground'}`}>
                  {user.name}
                </h3>
                <p className="text-sm text-muted-foreground">{user.points.toLocaleString()} points</p>
              </div>
              {user.isYou ? (
                <Badge variant="secondary" className="bg-primary/20 text-primary">
                  You
                </Badge>
              ) : (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => sendFriendRequest(user.username)}
                >
                  <UserPlus className="w-3 h-3 mr-1" />
                  Add Friend
                </Button>
              )}
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold bg-gradient-secondary bg-clip-text text-transparent">
          Leaderboard 🏆
        </h1>
        <p className="text-muted-foreground">Compete and climb the ranks!</p>
      </div>

      {/* Period Selector */}
      <div className="flex justify-center">
        <Tabs value={selectedPeriod} onValueChange={setSelectedPeriod} className="w-full max-w-md">
          <TabsList className="grid w-full grid-cols-3 bg-muted/50">
            <TabsTrigger value="daily" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
              Daily
            </TabsTrigger>
            <TabsTrigger value="weekly" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
              Weekly
            </TabsTrigger>
            <TabsTrigger value="alltime" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
              All Time
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Friend Search */}
      <Card className="bg-gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="w-5 h-5 text-primary" />
            <span>Find Friends</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search username to add as friend..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="pl-10"
            />
            {searchLoading && (
              <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 w-4 h-4 animate-spin" />
            )}
          </div>
          
          {searchResults.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Search Results:</p>
              {searchResults.map((user) => (
                <div
                  key={user.user_id}
                  className="flex items-center space-x-4 p-3 bg-muted/20 rounded-lg transition-all duration-300 hover:bg-muted/30"
                >
                  <div className="text-lg">{user.badge}</div>
                  <Avatar className="w-10 h-10">
                    <AvatarFallback className="bg-gradient-secondary text-secondary-foreground text-sm font-bold">
                      {user.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                    </AvatarFallback>
                  </Avatar>
                  <div className="flex-1">
                    <h4 className="font-semibold">{user.name}</h4>
                    <p className="text-xs text-muted-foreground">@{user.username}</p>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => sendFriendRequest(user.username)}
                  >
                    <UserPlus className="w-3 h-3 mr-1" />
                    Add Friend
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* User Points Display */}
      <Card className="bg-gradient-primary/10 border-primary/50">
        <CardContent className="p-6 text-center">
          <div className="text-4xl font-bold text-primary mb-2">{userPoints}</div>
          <p className="text-muted-foreground">Your Total Points</p>
        </CardContent>
      </Card>

      {/* Leaderboard Tabs */}
      <Tabs defaultValue="points" className="w-full">
        <TabsList className="grid w-full grid-cols-3 bg-muted/50">
          <TabsTrigger value="points" className="data-[state=active]:bg-secondary data-[state=active]:text-secondary-foreground">
            <Zap className="w-4 h-4 mr-2" />
            Points
          </TabsTrigger>
          <TabsTrigger value="global" className="data-[state=active]:bg-secondary data-[state=active]:text-secondary-foreground">
            <Users className="w-4 h-4 mr-2" />
            Global
          </TabsTrigger>
          <TabsTrigger value="friends" className="data-[state=active]:bg-secondary data-[state=active]:text-secondary-foreground">
            <Bell className="w-4 h-4 mr-2" />
            Friends
          </TabsTrigger>
        </TabsList>

        <TabsContent value="points" className="space-y-4 mt-6">
          {renderLeaderboard(pointsLeaderboard, "Points Leaderboard")}
        </TabsContent>

        <TabsContent value="global" className="space-y-4 mt-6">
          {renderLeaderboard(globalLeaderboard, "Global Rankings")}
        </TabsContent>

        <TabsContent value="friends" className="space-y-4 mt-6">
          {renderLeaderboard(friendsPoints, "Friends Points")}
        </TabsContent>
      </Tabs>

      {/* Achievement Badges */}
      <Card className="bg-gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Timer className="w-5 h-5 text-energy" />
            <span>Achievement Badges</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { icon: "🏃‍♂️", title: "Speed Demon", desc: "100 fast reps" },
              { icon: "💪", title: "Strength Beast", desc: "500 push-ups" },
              { icon: "🔥", title: "Consistency King", desc: "30-day streak" },
              { icon: "⚡", title: "Power Player", desc: "Top 10%" }
            ].map((badge) => (
              <div key={badge.title} className="text-center p-4 bg-primary/5 rounded-lg hover:bg-primary/10 transition-colors">
                <div className="text-3xl mb-2">{badge.icon}</div>
                <h4 className="font-semibold text-sm">{badge.title}</h4>
                <p className="text-xs text-muted-foreground">{badge.desc}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};