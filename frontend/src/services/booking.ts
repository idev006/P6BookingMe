import api from './api';

export interface Booking {
  id: number;
  room_id: number;
  user_id: number;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  status: string;
  snap_room_name: string;
  snap_room_location: string;
  snap_room_capacity: number;
}

export interface BookingCreateData {
  room_id: number;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  attendee_count: number;
}

const bookingService = {
  createBooking: (data: BookingCreateData) => 
    api.post('/bookings/', data),

  getMyBookings: (params: any = {}) => 
    api.get('/bookings/', { params }),

  getBookingDetail: (id: number) => 
    api.get(`/bookings/${id}`),

  cancelBooking: (id: number) => 
    api.post(`/bookings/${id}/cancel/`),

  updateBooking: (id: number, data: any) => 
    api.patch(`/bookings/${id}`, data),
};

export default bookingService;
