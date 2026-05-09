<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue';
import MainLayout from '../../components/layout/MainLayout.vue';
import api from '../../services/api';
import { useUIStore } from '../../stores/ui';
import { Calendar, Search, Filter, XCircle, Info, User, Clock, FileSpreadsheet, Eye } from 'lucide-vue-next';
import { formatDateTime, formatDate, formatTime } from '../../utils/format';
import BookingDetailModal from '../../components/booking/BookingDetailModal.vue';

const bookings = ref<any[]>([]);
const loading = ref(false);
const ui = useUIStore();
const isCancelModalOpen = ref(false);
const cancelBookingId = ref<number | null>(null);
const cancelReason = ref('');
const cancelDialogRef = ref<HTMLDialogElement | null>(null);

watch(isCancelModalOpen, (newVal) => {
  if (newVal) {
    cancelDialogRef.value?.showModal();
  } else {
    cancelDialogRef.value?.close();
  }
});

const handleCancelModalClose = () => {
  isCancelModalOpen.value = false;
};

const selectedBookingId = ref<number | null>(null);
const searchQuery = ref('');
const statusFilter = ref('all');

const isDetailModalOpen = ref(false);
const selectedBookingForDetail = ref<any | null>(null);

const handleExport = async () => {
  try {
    const response = await api.get('/admin/reporting/export/bookings/', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `bookings_export_all_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (err) {
    console.error('Export failed', err);
  }
};

const currentPage = ref(1);
const pageSize = ref(10);
const totalBookings = ref(0);
const pageSizeOptions = [5, 10, 15, 25, 50];

const filteredBookings = computed(() => bookings.value);

const fetchAllBookings = async () => {
  loading.value = true;
  try {
    const skip = (currentPage.value - 1) * pageSize.value;
    const params = {
      skip,
      limit: pageSize.value,
      search: searchQuery.value || undefined,
      status: statusFilter.value !== 'all' ? statusFilter.value : undefined
    };
    const response = await api.get('/admin/bookings/', { params });
    bookings.value = response.data.data.data;
    totalBookings.value = response.data.data.total;
  } catch (err) {
    console.error('Failed to fetch all bookings', err);
  } finally {
    loading.value = false;
  }
};

// Debounced search
let searchTimeout: any = null;
watch(searchQuery, () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    currentPage.value = 1;
    fetchAllBookings();
  }, 500);
});

watch([statusFilter, pageSize], () => {
  currentPage.value = 1;
  fetchAllBookings();
});

onMounted(fetchAllBookings);

const openDetail = (booking: any) => {
  selectedBookingForDetail.value = booking;
  isDetailModalOpen.value = true;
};

const openCancelModal = (id: number) => {
  selectedBookingId.value = id;
  cancelReason.value = '';
  isCancelModalOpen.value = true;
};

const handleAdminCancel = async () => {
  if (!cancelReason.value) {
    ui.showAlert({ title: 'คำเตือน', message: 'กรุณาระบุเหตุผลการยกเลิก', type: 'warning' });
    return;
  }
  
  try {
    await api.post(`/admin/bookings/${selectedBookingId.value}/cancel/`, { reason: cancelReason.value });
    ui.showAlert({ title: 'สำเร็จ', message: 'ยกเลิกการจองเรียบร้อยแล้ว', type: 'success' });
    isCancelModalOpen.value = false;
    fetchAllBookings();
  } catch (err: any) {
    ui.showAlert({ title: 'ผิดพลาด', message: err.response?.data?.detail || 'เกิดข้อผิดพลาด', type: 'error' });
  }
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'confirmed': return 'badge-success';
    case 'pending': return 'badge-warning';
    case 'cancelled': return 'badge-neutral';
    case 'rejected': return 'badge-error';
    default: return 'badge-ghost';
  }
};
</script>

<template>
  <MainLayout>
    <div class="animate-fade-in">
      <header class="mb-10 flex flex-col xl:flex-row justify-between items-start xl:items-end gap-6">
        <div>
          <h1 class="text-3xl font-black text-base-content mb-2 flex items-center gap-3 tracking-tight">
            <Calendar class="text-primary" :size="32" />
            รายการจองทั้งหมด
          </h1>
          <p class="text-base-content/60 font-medium">จัดการรายการจองของพนักงานทุกคนในองค์กร</p>
        </div>

        <div class="flex flex-col sm:flex-row w-full xl:w-auto gap-4">
          <!-- Status Filter -->
          <div class="flex items-center gap-3 bg-base-200/50 px-4 rounded-2xl border border-base-content/5 h-12">
            <Filter :size="14" class="opacity-40" />
            <select v-model="statusFilter" class="select select-ghost select-xs font-black focus:outline-none bg-transparent">
              <option value="all">ทุกสถานะ</option>
              <option value="pending">รออนุมัติ</option>
              <option value="confirmed">อนุมัติแล้ว</option>
              <option value="rejected">ปฏิเสธแล้ว</option>
              <option value="cancelled">ยกเลิกแล้ว</option>
            </select>
          </div>

          <!-- Search Input -->
          <div class="relative flex-grow sm:w-64 group">
            <Search :size="18" class="absolute left-4 top-1/2 -translate-y-1/2 text-base-content/30 group-focus-within:text-primary transition-colors" />
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="ค้นหาห้องหรือผู้จอง..." 
              class="input input-bordered w-full pl-12 h-12 rounded-2xl bg-base-100 border-base-content/10 focus:border-primary/30 transition-all font-medium shadow-sm"
            />
          </div>

          <button @click="handleExport" class="btn btn-primary h-12 px-6 rounded-2xl gap-2 shadow-lg shadow-primary/20 font-black">
            <FileSpreadsheet :size="18" /> ส่งออก CSV
          </button>
        </div>
      </header>

      <div class="card bg-base-100 shadow-2xl border border-base-content/5 overflow-hidden">
        <div class="p-4 border-b border-base-content/5 flex justify-end">
           <div class="flex items-center gap-3 bg-base-200/50 px-4 rounded-xl border border-base-content/5 h-10">
            <Filter :size="14" class="opacity-40" />
            <span class="text-[10px] font-black uppercase tracking-widest opacity-40">ROWS:</span>
            <select v-model="pageSize" class="select select-bordered select-xs font-black focus:outline-none bg-base-100 border-base-content/10">
              <option v-for="opt in pageSizeOptions" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="table table-lg w-full">
            <thead>
              <tr class="bg-base-200/50">
                <th class="py-5 pl-8 font-black uppercase text-[10px] tracking-widest opacity-40">หัวข้อ / ห้องประชุม</th>
                <th class="py-5 font-black uppercase text-[10px] tracking-widest opacity-40">ผู้จอง</th>
                <th class="py-5 font-black uppercase text-[10px] tracking-widest opacity-40">วัน-เวลา</th>
                <th class="py-5 font-black uppercase text-[10px] tracking-widest opacity-40">สถานะ</th>
                <th class="py-5 font-black uppercase text-[10px] tracking-widest opacity-40 text-right pr-8">จัดการ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="booking in filteredBookings" :key="booking.id" 
                  @click="openDetail(booking)"
                  class="hover:bg-primary/5 transition-colors border-b border-base-content/5 cursor-pointer group">
                <td class="pl-8">
                  <div class="flex items-center gap-4">
                    <div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center text-primary font-black group-hover:bg-primary group-hover:text-white transition-all shadow-sm">
                      {{ booking.snap_room_name.charAt(0) }}
                    </div>
                    <div>
                      <div class="font-black text-lg leading-tight tracking-tight group-hover:text-primary transition-colors">{{ booking.title }}</div>
                      <div class="text-[10px] opacity-40 font-black uppercase tracking-widest flex items-center gap-1 mt-1">
                        <Info :size="12" /> {{ booking.snap_room_name }}
                      </div>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-full bg-base-200 flex items-center justify-center text-[10px] font-black">
                      {{ booking.snap_user_name.charAt(0) }}
                    </div>
                    <span class="text-xs font-bold">{{ booking.snap_user_name }}</span>
                  </div>
                </td>
                <td>
                  <div class="flex flex-col gap-1 py-1">
                    <div class="flex items-center gap-2 font-bold text-xs">
                      <Calendar :size="12" class="text-primary" />
                      {{ formatDate(booking.start_time) }}
                    </div>
                    <div class="flex items-center gap-2 text-[10px] font-black opacity-40">
                      <Clock :size="12" />
                      {{ formatTime(booking.start_time) }} - {{ formatTime(booking.end_time) }}
                    </div>
                  </div>
                </td>
                <td>
                  <div :class="['badge badge-sm font-black uppercase text-[10px] tracking-widest p-3 shadow-sm', getStatusBadge(booking.status)]">
                    {{ booking.status }}
                  </div>
                </td>
                <td class="text-right pr-8" @click.stop>
                  <div class="flex justify-end gap-1">
                    <button @click="openDetail(booking)" class="btn btn-ghost btn-sm btn-square text-primary tooltip" data-tip="ดูรายละเอียด">
                      <Eye :size="20" />
                    </button>
                    
                    <button 
                      v-if="booking.status === 'confirmed' || booking.status === 'pending'" 
                      @click="openCancelModal(booking.id)" 
                      class="btn btn-ghost btn-sm btn-square text-error tooltip" 
                      data-tip="ยกเลิกการจอง"
                    >
                      <XCircle :size="20" />
                    </button>
                    <button v-else class="btn btn-ghost btn-sm btn-square opacity-10 cursor-not-allowed">
                      <XCircle :size="20" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination Footer -->
        <div v-if="totalBookings > 0" class="p-6 bg-base-200/20 border-t border-base-content/5 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div class="text-xs font-black opacity-40 uppercase tracking-widest">
            Showing {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, totalBookings) }} of {{ totalBookings }} Bookings
          </div>

          <div class="join shadow-sm border border-base-content/5">
            <button 
              class="join-item btn btn-sm px-6 bg-base-100 border-0 hover:bg-primary hover:text-white" 
              :disabled="currentPage === 1"
              @click="currentPage--; fetchAllBookings()"
            >PREV</button>
            <button class="join-item btn btn-sm px-6 bg-base-100 border-0 font-black">PAGE {{ currentPage }}</button>
            <button 
              class="join-item btn btn-sm px-6 bg-base-100 border-0 hover:bg-primary hover:text-white" 
              :disabled="currentPage * pageSize >= totalBookings"
              @click="currentPage++; fetchAllBookings()"
            >NEXT</button>
          </div>
        </div>

        <div v-if="filteredBookings.length === 0 && !loading" class="py-32 text-center flex flex-col items-center">
          <div class="w-20 h-20 bg-base-200 rounded-full flex items-center justify-center text-base-content/20 mb-6">
            <Search :size="40" />
          </div>
          <h3 class="text-2xl font-black opacity-20 uppercase tracking-widest">ไม่พบข้อมูลการจอง</h3>
          <p class="text-sm opacity-30 mt-2">ลองเปลี่ยนคำค้นหาหรือตัวกรองเพื่อหาข้อมูลที่คุณต้องการ</p>
          <button @click="searchQuery = ''; statusFilter = 'all'" class="btn btn-ghost btn-sm mt-4 text-primary font-black uppercase tracking-widest">ล้างการค้นหา</button>
        </div>
      </div>
    </div>

    <!-- Booking Detail Modal -->
    <BookingDetailModal 
      :is-open="isDetailModalOpen" 
      :booking="selectedBookingForDetail" 
      @close="isDetailModalOpen = false" 
    />

    <!-- Admin Cancel Modal -->
    <dialog ref="cancelDialogRef" class="modal" @close="handleCancelModalClose">
      <div class="modal-box bg-base-100 border border-base-content/10 shadow-2xl">
        <h3 class="font-bold text-2xl mb-4 text-error">ระบุเหตุผลการยกเลิก</h3>
        <p class="py-4 text-base-content/70">การยกเลิกโดยผู้ดูแลระบบจำเป็นต้องระบุเหตุผลเพื่อแจ้งให้พนักงานทราบ</p>
        
        <textarea 
          v-model="cancelReason" 
          class="textarea textarea-bordered w-full h-32 focus:textarea-error" 
          placeholder="เช่น ห้องถูกปิดซ่อมบำรุงด่วน, มีการจองซ้ำซ้อนระดับบริหาร..."
        ></textarea>

        <div class="modal-action gap-2">
          <button class="btn btn-ghost" @click="isCancelModalOpen = false">ยกเลิก</button>
          <button class="btn btn-error px-8 shadow-lg shadow-error/20" @click="handleAdminCancel">
            ยืนยันการยกเลิกโดย Admin
          </button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="isCancelModalOpen = false">
        <button>close</button>
      </form>
    </dialog>
  </MainLayout>
</template>
