import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Bell, UserPlus, Activity, Calendar, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { notificationsAPI } from "@/lib/api";

interface Notification {
  id: string;
  type: 'friend_request' | 'workout_progress' | 'workout_plan';
  title: string;
  message: string;
  timestamp: Date;
  data?: any;
  read: boolean;
}

interface FriendRequest {
  id: string;
  from: string;
  timestamp: Date;
}

export const NotificationBell = ({ user }: { user?: any }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [friendRequests, setFriendRequests] = useState<FriendRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (user?.username) {
      loadNotifications();
      loadFriendRequests();
    }
  }, [user]);

  const loadNotifications = async () => {
    try {
      const notifications = await notificationsAPI.getNotifications();
      setNotifications(notifications.map((n: any) => ({ 
        ...n, 
        timestamp: n.timestamp ? new Date(n.timestamp) : new Date() 
      })));
    } catch (error) {
      console.error('Error loading notifications:', error);
      // Fallback to localStorage if API fails
      const stored = localStorage.getItem(`notifications-${user?.username}`);
      if (stored) {
        const parsed = JSON.parse(stored);
        setNotifications(parsed.map((n: any) => ({ 
          ...n, 
          timestamp: n.timestamp ? new Date(n.timestamp) : new Date() 
        })));
      }
    }
  };

  const loadFriendRequests = async () => {
    try {
      const requests = await notificationsAPI.getFriendRequests();
      setFriendRequests(requests.map((fr: any) => ({ 
        ...fr, 
        timestamp: fr.timestamp ? new Date(fr.timestamp) : new Date() 
      })));
    } catch (error) {
      console.error('Error loading friend requests:', error);
      // Fallback to localStorage if API fails
      const stored = localStorage.getItem(`friendRequests-${user?.username}`);
      if (stored) {
        const parsed = JSON.parse(stored);
        setFriendRequests(parsed.map((fr: any) => ({ 
          ...fr, 
          timestamp: fr.timestamp ? new Date(fr.timestamp) : new Date() 
        })));
      }
    }
  };

  const addNotification = async (notificationData: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    try {
      const newNotification = await notificationsAPI.createNotification(notificationData);
      setNotifications(prev => [newNotification, ...prev]);
    } catch (error) {
      console.error('Error creating notification:', error);
      // Fallback to localStorage
      const newNotification: Notification = {
        ...notificationData,
        id: Date.now().toString(),
        timestamp: new Date(),
        read: false
      };

      setNotifications(prev => {
        const updated = [newNotification, ...prev];
        localStorage.setItem(`notifications-${user?.username}`, JSON.stringify(updated));
        return updated;
      });
    }
  };

  const handleFriendRequest = async (requestId: string, action: 'accept' | 'reject') => {
    const request = friendRequests.find(fr => fr.id === requestId);
    if (!request) return;

    setLoading(true);
    try {
      if (action === 'accept') {
        // Respond to friend request via API
        await notificationsAPI.respondToFriendRequest(requestId, 'accept');
        
        toast({
          title: "Friend Added!",
          description: `You are now friends with ${request.from}`
        });
      } else {
        // Reject friend request via API
        await notificationsAPI.respondToFriendRequest(requestId, 'reject');
        
        toast({
          title: "Request Rejected",
          description: `Friend request from ${request.from} was rejected`
        });
      }

      // Reload friend requests and notifications
      await loadFriendRequests();
      await loadNotifications();

    } catch (error) {
      console.error('Error handling friend request:', error);
      toast({
        title: "Error",
        description: "Failed to process friend request",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId: string) => {
    try {
      await notificationsAPI.markAsRead(notificationId);
      setNotifications(prev => {
        const updated = prev.map(n => 
          n.id === notificationId ? { ...n, read: true } : n
        );
        return updated;
      });
    } catch (error) {
      console.error('Error marking notification as read:', error);
      // Fallback to local update
      setNotifications(prev => {
        const updated = prev.map(n => 
          n.id === notificationId ? { ...n, read: true } : n
        );
        localStorage.setItem(`notifications-${user?.username}`, JSON.stringify(updated));
        return updated;
      });
    }
  };

  // Generate workout progress notification when workout is completed
  const generateWorkoutNotification = async (workoutData: any) => {
    await addNotification({
      type: 'workout_progress',
      title: 'Workout Completed!',
      message: `Great job! You completed ${workoutData.reps} reps of ${workoutData.exercise} with ${workoutData.accuracy}% accuracy.`,
      data: workoutData
    });
  };

  // Generate workout plan notification
  const generateWorkoutPlanNotification = async (planData: any) => {
    await addNotification({
      type: 'workout_plan',
      title: "New Workout Plan Available!",
      message: `Your personalized ${planData.category} workout plan is ready with ${planData.exercises?.length || 0} exercises.`,
      data: planData
    });
  };

  // Expose these functions for other components to use
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).generateWorkoutNotification = generateWorkoutNotification;
      (window as any).generateWorkoutPlanNotification = generateWorkoutPlanNotification;
    }
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length + friendRequests.length;

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'friend_request': return <UserPlus className="w-4 h-4" />;
      case 'workout_progress': return <Activity className="w-4 h-4" />;
      case 'workout_plan': return <Calendar className="w-4 h-4" />;
      default: return <Bell className="w-4 h-4" />;
    }
  };

  if (!user?.username) {
    return null;
  }

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon-sm" className="relative">
          <Bell className="w-5 h-5" />
          {unreadCount > 0 && (
            <Badge className="absolute -top-1 -right-1 w-5 h-5 rounded-full p-0 flex items-center justify-center text-xs bg-destructive">
              {unreadCount}
            </Badge>
          )}
        </Button>
      </SheetTrigger>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Notifications</SheetTitle>
          <SheetDescription>
            Stay updated with your fitness journey and friends
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-4 mt-6">
          {loading && (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
              <span className="text-sm text-muted-foreground">Processing...</span>
            </div>
          )}

          {/* Friend Requests */}
          {friendRequests.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-muted-foreground">Friend Requests</h3>
              {friendRequests.map((request) => (
                <Card key={request.id} className="bg-primary/5">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <UserPlus className="w-4 h-4 text-primary" />
                        <div>
                          <p className="text-sm font-medium">{request.from}</p>
                          <p className="text-xs text-muted-foreground">Wants to be friends</p>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleFriendRequest(request.id, 'accept')}
                          disabled={loading}
                        >
                          Accept
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleFriendRequest(request.id, 'reject')}
                          disabled={loading}
                        >
                          Reject
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* Other Notifications */}
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-muted-foreground">Updates</h3>
            {notifications.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                No notifications yet
              </p>
            ) : (
              notifications.map((notification) => (
                <Card
                  key={notification.id}
                  className={`cursor-pointer transition-colors ${
                    notification.read ? 'bg-card' : 'bg-primary/5'
                  }`}
                  onClick={() => markAsRead(notification.id)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start space-x-3">
                      <div className="mt-1">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="flex-1">
                        <h4 className="text-sm font-medium">{notification.title}</h4>
                        <p className="text-xs text-muted-foreground mt-1">
                          {notification.message}
                        </p>
                        <p className="text-xs text-muted-foreground mt-2">
                          {notification.timestamp ? 
                            (notification.timestamp instanceof Date ? 
                              notification.timestamp.toLocaleTimeString() : 
                              new Date(notification.timestamp).toLocaleTimeString()
                            ) : 
                            'Just now'
                          }
                        </p>
                      </div>
                      {!notification.read && (
                        <div className="w-2 h-2 bg-primary rounded-full mt-1" />
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
};
