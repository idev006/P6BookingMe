import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import roomService from '../services/room';
import type { Room } from '../services/room';

export const useRoomStore = defineStore('room', () => {
  // State
  const rooms = ref<Room[]>([]);
  const selectedRoom = ref<Room | null>(null);
  const loading = ref(false);
  const total = ref(0);
  const lastFetched = ref<number | null>(null);

  // Getters
  const getRoomById = computed(() => (id: number) => {
    return rooms.value.find(r => r.id === id) || null;
  });

  // Actions
  const fetchRooms = async (params: any = {}, force = false) => {
    // Basic caching: don't fetch if fetched within last 30 seconds
    const now = Date.now();
    if (!force && lastFetched.value && (now - lastFetched.value < 30000) && rooms.value.length > 0) {
      return;
    }

    loading.value = true;
    try {
      const data = await roomService.getRooms(params);
      // Backend returns StandardResponse with { data: { data: [...], total: X } }
      rooms.value = data.data.data || [];
      total.value = data.data.total || 0;
      lastFetched.value = now;
    } catch (err) {
      console.error('Failed to fetch rooms', err);
    } finally {
      loading.value = false;
    }
  };

  const fetchRoomDetail = async (id: number) => {
    // Check if we already have it in state
    const existing = rooms.value.find(r => r.id === id);
    if (existing) {
      selectedRoom.value = existing;
    }

    loading.value = true;
    try {
      const room = await roomService.getRoom(id);
      selectedRoom.value = room;
      
      // Update the item in the list if it exists
      const index = rooms.value.findIndex(r => r.id === id);
      if (index !== -1) {
        rooms.value[index] = room;
      }
    } catch (err) {
      console.error('Failed to fetch room detail', err);
    } finally {
      loading.value = false;
    }
  };

  const clearCache = () => {
    lastFetched.value = null;
    rooms.value = [];
  };

  return {
    rooms,
    selectedRoom,
    loading,
    total,
    getRoomById,
    fetchRooms,
    fetchRoomDetail,
    clearCache
  };
});
