import api from './api';

export interface Notification {
  id: number;
  type: string;
  message: string;
  is_read: boolean;
  created_at: string;
  booking_id?: number;
}

const notificationService = {
  getNotifications: (limit: number = 10) => 
    api.get(`/notifications/?limit=${limit}`),
    
  markAllRead: () => 
    api.post('/notifications/read-all'),
};

export default notificationService;
