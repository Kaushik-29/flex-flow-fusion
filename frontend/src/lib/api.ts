const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Helper function to get auth token
const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

// Helper function to make authenticated requests
const authFetch = async (url: string, options: RequestInit = {}) => {
  const token = getAuthToken();
  
  if (!token) {
    throw new Error('No authentication token found. Please log in again.');
  }
  
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    ...options.headers,
  };

  console.log(`Making authenticated request to: ${API_BASE_URL}${url}`);
  console.log('Token present:', !!token);

  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    console.error(`API Error: ${response.status} ${response.statusText}`);
    console.error('Response headers:', Object.fromEntries(response.headers.entries()));
    
    if (response.status === 401) {
      // Clear invalid token
      localStorage.removeItem('authToken');
      localStorage.removeItem('currentUser');
      throw new Error('Authentication failed. Please log in again.');
    }
    
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
};

// Authentication API
export const authAPI = {
  register: async (userData: { name: string; username: string; email: string; password: string }) => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });
    return response.json();
  },

  login: async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  },

  getMe: async () => {
    return authFetch('/auth/me');
  },
};

// Leaderboard API
export const leaderboardAPI = {
  getTop: async (period: string = 'alltime', limit: number = 10) => {
    return authFetch(`/leaderboard/top?period=${period}&limit=${limit}`);
  },

  searchUsers: async (query: string) => {
    return authFetch(`/leaderboard/search?query=${encodeURIComponent(query)}`);
  },
};

// Friends API
export const friendsAPI = {
  sendRequest: async (friendUsername: string) => {
    return authFetch('/auth/friends/request', {
      method: 'POST',
      body: JSON.stringify({ friend_username: friendUsername }),
    });
  },

  getRequests: async () => {
    return authFetch('/auth/friends/requests');
  },

  respondToRequest: async (requestId: string, action: 'accept' | 'reject') => {
    return authFetch(`/auth/friends/request/${requestId}/respond`, {
      method: 'POST',
      body: JSON.stringify({ request_id: requestId, action }),
    });
  },

  getFriends: async () => {
    return authFetch('/auth/friends');
  },
};

// Workout API
export const workoutAPI = {
  start: async (type: string) => {
    return authFetch('/workout/start', {
      method: 'POST',
      body: JSON.stringify({ type }),
    });
  },

  update: async (sessionId: string, reps: number, accuracy: number, feedback: string) => {
    return authFetch('/workout/update', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, reps, accuracy, feedback }),
    });
  },

  getHistory: async () => {
    return authFetch('/workout/history');
  },
};

// Pose Feedback API
export const poseFeedbackAPI = {
  getFeedback: async (poseData: { pose_type: string; keypoints: any[]; user_id: string }) => {
    return authFetch('/pose-feedback', {
      method: 'POST',
      body: JSON.stringify(poseData),
    });
  },
};

// Notifications API
export const notificationsAPI = {
  getNotifications: async () => {
    return authFetch('/notifications');
  },

  createNotification: async (notification: { type: string; title: string; message: string; data?: any }) => {
    return authFetch('/notifications', {
      method: 'POST',
      body: JSON.stringify(notification),
    });
  },

  markAsRead: async (notificationId: string) => {
    return authFetch(`/notifications/${notificationId}/read`, {
      method: 'PUT',
    });
  },

  deleteNotification: async (notificationId: string) => {
    return authFetch(`/notifications/${notificationId}`, {
      method: 'DELETE',
    });
  },

  getFriendRequests: async () => {
    return authFetch('/notifications/friend-requests');
  },

  sendFriendRequest: async (toUsername: string) => {
    return authFetch('/auth/friends/request', {
      method: 'POST',
      body: JSON.stringify({ friend_username: toUsername }),
    });
  },

  respondToFriendRequest: async (requestId: string, action: 'accept' | 'reject') => {
    return authFetch(`/auth/friends/request/${requestId}/respond`, {
      method: 'POST',
      body: JSON.stringify({ request_id: requestId, action }),
    });
  },

  getUnreadCount: async () => {
    return authFetch('/notifications/unread-count');
  },
};

// Points API
export const pointsAPI = {
  calculatePoints: async (exercise: string, repsCompleted: number) => {
    return authFetch(`/points/calculate?exercise=${encodeURIComponent(exercise)}&reps_completed=${repsCompleted}`, {
      method: 'POST',
    });
  },

  getUserPoints: async () => {
    return authFetch('/points/user');
  },

  getPointsLeaderboard: async (limit: number = 50) => {
    return authFetch(`/points/leaderboard?limit=${limit}`);
  },

  getFriendsPoints: async () => {
    return authFetch('/points/friends');
  },

  getPointsHistory: async (exercise?: string, limit: number = 20) => {
    const params = new URLSearchParams();
    if (exercise) params.append('exercise', exercise);
    params.append('limit', limit.toString());
    return authFetch(`/points/history?${params.toString()}`);
  },

  getExerciseConfigs: async () => {
    return authFetch('/points/config');
  },
}; 