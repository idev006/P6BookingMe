import { defineStore } from 'pinia';
import { ref } from 'vue';
import bookingService from '../services/booking';
import type { Booking } from '../services/booking';

export const useBookingStore = defineStore('booking', () => {
  const myBookings = ref<Booking[]>([]);
  const total = ref(0);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchMyBookings = async (params: any = {}) => {
    loading.value = true;
    try {
      const response = await bookingService.getMyBookings(params);
      // Handle paginated response: { data: { total: X, data: [...] } }
      myBookings.value = response.data.data.data || [];
      total.value = response.data.data.total || 0;
    } catch (err: any) {
      error.value = 'ไม่สามารถโหลดข้อมูลการจองได้';
    } finally {
      loading.value = false;
    }
  };

  const createBooking = async (bookingData: any) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await bookingService.createBooking(bookingData);
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'การจองล้มเหลว';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const cancelBooking = async (id: number) => {
    loading.value = true;
    try {
      await bookingService.cancelBooking(id);
      // Update local state
      const booking = myBookings.value.find(b => b.id === id);
      if (booking) booking.status = 'cancelled';
    } catch (err: any) {
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getBookingDetail = async (id: number) => {
    loading.value = true;
    try {
      const response = await bookingService.getBookingDetail(id);
      return response.data.data;
    } catch (err) {
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const updateBooking = async (id: number, data: any) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await bookingService.updateBooking(id, data);
      return response.data.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'แก้ไขการจองล้มเหลว';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    myBookings,
    total,
    loading,
    error,
    fetchMyBookings,
    createBooking,
    cancelBooking,
    getBookingDetail,
    updateBooking
  };
});
