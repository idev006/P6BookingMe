import api from './api';

export interface RoomEquipment {
  id: number;
  name: string;
}

export interface RoomImage {
  id: number;
  image_path: string;
  is_primary: boolean;
}

export interface Room {
  id: number;
  name: string;
  capacity: number;
  location: string;
  building: string | null;
  floor: string | null;
  description: string | null;
  status: 'active' | 'inactive';
  created_at: string;
  updated_at: string;
  equipment: RoomEquipment[];
  images: RoomImage[];
}

export interface RoomCreateData {
  name: string;
  capacity: number;
  location: string;
  building?: string;
  floor?: string;
  description?: string;
  equipment?: string[];
}

export default {
  async getRooms(params: any = {}) {
    const response = await api.get('/rooms', { params });
    return response.data;
  },

  async getRoom(id: number) {
    const response = await api.get(`/rooms/${id}`);
    return response.data;
  },

  async createRoom(data: RoomCreateData) {
    const response = await api.post('/rooms', data);
    return response.data;
  },

  async updateRoom(id: number, data: any) {
    const response = await api.patch(`/rooms/${id}`, data);
    return response.data;
  },

  async deactivateRoom(id: number) {
    const response = await api.post(`/rooms/${id}/deactivate`);
    return response.data;
  },

  async activateRoom(id: number) {
    const response = await api.post(`/rooms/${id}/activate`);
    return response.data;
  },

  // Image Management
  async uploadImage(roomId: number, file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/rooms/${roomId}/images`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async deleteImage(roomId: number, imageId: number) {
    await api.delete(`/rooms/${roomId}/images/${imageId}`);
  },

  async setPrimaryImage(roomId: number, imageId: number) {
    const response = await api.post(`/rooms/${roomId}/images/${imageId}/set-primary`);
    return response.data;
  },
};
