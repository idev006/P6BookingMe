import api from './api';

const roomAdminService = {
  createRoom: (data: any) => 
    api.post('/rooms', data),
    
  updateRoom: (id: number, data: any) => 
    api.patch(`/rooms/${id}`, data),
    
  deleteRoom: (id: number) => 
    api.delete(`/rooms/${id}`),
    
  uploadImage: (roomId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/rooms/${roomId}/images`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
  
  deleteImage: (roomId: number, imageId: number) => 
    api.delete(`/rooms/${roomId}/images/${imageId}`),
};

export default roomAdminService;
