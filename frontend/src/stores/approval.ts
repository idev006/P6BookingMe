import { defineStore } from 'pinia';
import { ref } from 'vue';
import approvalService from '../services/approval';
import type { Booking } from '../services/booking';

export const useApprovalStore = defineStore('approval', () => {
  const pendingBookings = ref<Booking[]>([]);
  const loading = ref(false);
  const total = ref(0);
  const summary = ref<any>(null);

  const fetchSummary = async () => {
    loading.value = true;
    try {
      const response = await approvalService.getSummary();
      summary.value = response.data.data;
    } catch (err) {
      console.error('Failed to fetch approval summary', err);
    } finally {
      loading.value = false;
    }
  };

  const fetchPendingBookings = async (params: any = {}) => {
    loading.value = true;
    try {
      const response = await approvalService.getPendingBookings(params);
      pendingBookings.value = response.data.data.data;
      total.value = response.data.data.total;
    } catch (err) {
      console.error('Failed to fetch pending bookings', err);
    } finally {
      loading.value = false;
    }
  };

  const approve = async (id: number, note?: string) => {
    loading.value = true;
    try {
      await approvalService.approveBooking(id, note);
      pendingBookings.value = pendingBookings.value.filter(b => b.id !== id);
      total.value--;
      // Refresh summary if on dashboard
      if (summary.value) fetchSummary();
    } catch (err) {
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const reject = async (id: number, note: string) => {
    loading.value = true;
    try {
      await approvalService.rejectBooking(id, note);
      pendingBookings.value = pendingBookings.value.filter(b => b.id !== id);
      total.value--;
      // Refresh summary if on dashboard
      if (summary.value) fetchSummary();
    } catch (err) {
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    pendingBookings,
    loading,
    total,
    summary,
    fetchSummary,
    fetchPendingBookings,
    approve,
    reject
  };
});
