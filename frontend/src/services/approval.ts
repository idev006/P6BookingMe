import api from './api';

const approvalService = {
  getPendingBookings: (params: any = {}) => 
    api.get('/approvals/pending', { params }),
    
  approveBooking: (id: number, note?: string) => 
    api.post(`/approvals/${id}/approve`, { note }),
    
  rejectBooking: (id: number, note: string) => 
    api.post(`/approvals/${id}/reject`, { note }),

  getSummary: () =>
    api.get('/approvals/summary'),
};

export default approvalService;
