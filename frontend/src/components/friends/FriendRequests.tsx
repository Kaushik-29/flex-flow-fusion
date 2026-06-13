import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Users, UserPlus, UserCheck, UserX, Clock } from "lucide-react";
import { friendsAPI } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface FriendRequest {
  id: string;
  from_username: string;
  to_username: string;
  status: string;
  created_at: string;
}

interface FriendRequestsData {
  incoming: FriendRequest[];
  outgoing: FriendRequest[];
}

export const FriendRequests = () => {
  const [requests, setRequests] = useState<FriendRequestsData>({ incoming: [], outgoing: [] });
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  const fetchRequests = async () => {
    // Check if auth token exists
    const token = localStorage.getItem('authToken');
    console.log('FriendRequests: Auth token exists:', !!token);
    
    if (!token) {
      console.error('FriendRequests: No auth token found');
      setLoading(false);
      toast({
        title: "Authentication Error",
        description: "Please log in again to view friend requests",
        variant: "destructive",
      });
      return;
    }

    try {
      const data = await friendsAPI.getRequests();
      setRequests(data);
    } catch (error) {
      console.error("Error fetching friend requests:", error);
      toast({
        title: "Error",
        description: "Failed to load friend requests",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleRespond = async (requestId: string, action: 'accept' | 'reject') => {
    try {
      await friendsAPI.respondToRequest(requestId, action);
      
      toast({
        title: "Success",
        description: `Friend request ${action}ed successfully`,
      });
      
      // Refresh the requests
      fetchRequests();
    } catch (error) {
      console.error(`Error ${action}ing friend request:`, error);
      toast({
        title: "Error",
        description: `Failed to ${action} friend request`,
        variant: "destructive",
      });
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <Card className="bg-gradient-card border-border/50">
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <span className="ml-2">Loading friend requests...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Incoming Requests */}
      <Card className="bg-gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <UserPlus className="w-5 h-5 text-primary" />
            <span>Incoming Friend Requests</span>
            {requests.incoming.length > 0 && (
              <Badge variant="secondary" className="ml-2">
                {requests.incoming.length}
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {requests.incoming.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No incoming friend requests</p>
            </div>
          ) : (
            <div className="space-y-4">
              {requests.incoming.map((request) => (
                <div key={request.id} className="flex items-center justify-between p-4 bg-primary/5 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary/20 rounded-full flex items-center justify-center">
                      <Users className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">{request.from_username}</p>
                      <p className="text-sm text-muted-foreground flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {formatDate(request.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      size="sm"
                      onClick={() => handleRespond(request.id, 'accept')}
                      className="flex items-center space-x-1"
                    >
                      <UserCheck className="w-4 h-4" />
                      <span>Accept</span>
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      onClick={() => handleRespond(request.id, 'reject')}
                      className="flex items-center space-x-1"
                    >
                      <UserX className="w-4 h-4" />
                      <span>Reject</span>
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Outgoing Requests */}
      <Card className="bg-gradient-card border-border/50">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <UserPlus className="w-5 h-5 text-secondary" />
            <span>Outgoing Friend Requests</span>
            {requests.outgoing.length > 0 && (
              <Badge variant="secondary" className="ml-2">
                {requests.outgoing.length}
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {requests.outgoing.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No outgoing friend requests</p>
            </div>
          ) : (
            <div className="space-y-4">
              {requests.outgoing.map((request) => (
                <div key={request.id} className="flex items-center justify-between p-4 bg-secondary/5 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-secondary/20 rounded-full flex items-center justify-center">
                      <Users className="w-5 h-5 text-secondary" />
                    </div>
                    <div>
                      <p className="font-medium">{request.to_username}</p>
                      <p className="text-sm text-muted-foreground flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {formatDate(request.created_at)}
                      </p>
                    </div>
                  </div>
                  <Badge variant="outline" className="text-muted-foreground">
                    Pending
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}; 