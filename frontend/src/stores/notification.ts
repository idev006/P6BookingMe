import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import notificationService from '../services/notification';
import type { Notification } from '../services/notification';

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([]);
  const loading = ref(false);

  const unreadCount = computed(() => 
    notifications.value.filter(n => !n.is_read).length
  );

  const fetchNotifications = async () => {
    loading.value = true;
    try {
      const response = await notificationService.getNotifications();
      notifications.value = response.data.data;
    } catch (err) {
      console.error('Failed to fetch notifications', err);
    } finally {
      loading.value = false;
    }
  };

  const markAllRead = async () => {
    try {
      await notificationService.markAllRead();
      notifications.value.forEach(n => n.is_read = true);
    } catch (err) {
      console.error('Failed to mark all as read', err);
    }
  };

  return {
    notifications,
    unreadCount,
    loading,
    fetchNotifications,
    markAllRead
  };
});
