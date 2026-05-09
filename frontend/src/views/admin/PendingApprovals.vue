<script setup lang="ts">
import { onMounted, ref, watch, computed } from 'vue';
import MainLayout from '../../components/layout/MainLayout.vue';
import { useApprovalStore } from '../../stores/approval';
import { useUIStore } from '../../stores/ui';
import { CheckCircle, XCircle, Clock, Users, Calendar, MessageSquare, Info, Eye } from 'lucide-vue-next';
import { formatDateTime, formatDate, formatTime } from '../../utils/format';
import BookingDetailModal from '../../components/booking/BookingDetailModal.vue';

const approvalStore = useApprovalStore();
const ui = useUIStore();
const selectedBookingId = ref<number | null>(null);
const actionNote = ref('');
const isRejectModalOpen = ref(false);
const rejectDialogRef = ref<HTMLDialogElement | null>(null);

watch(isRejectModalOpen, (newVal) => {
  if (newVal) {
    rejectDialogRef.value?.showModal();
  } else {
    rejectDialogRef.value?.close();
  }
});

const handleRejectModalClose = () => {
  isRejectModalOpen.value = false;
};

const isDetailModalOpen = ref(false);
const selectedBookingForDetail = ref<any | null>(null);

// Search and Pagination States
const searchQuery = ref('');
const currentPage = ref(1);
const pageSize = ref(10);
const pageSizeOptions = [6, 12, 24, 48];

const fetchPendingBookings = async () => {
  const params = {
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value,
    search: searchQuery.value || undefined
  };
  await approvalStore.fetchPendingBookings(params);
};

// Debounced search
let searchTimeout: any = null;
watch(searchQuery, () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    currentPage.value = 1;
    fetchPendingBookings();
  }, 500);
});

watch(pageSize, () => {
  currentPage.value = 1;
  fetchPendingBookings();
});

onMounted(fetchPendingBookings);

const totalPages = computed(() => Math.ceil(approvalStore.total / pageSize.value));

const openDetail = (booking: any) => {
  selectedBookingForDetail.value = booking;
  isDetailModalOpen.value = true;
};

const handleApprove = (id: number) => {
  ui.showConfirm({
    title: 'ยืนยันการอนุมัติ',
    message: 'คุณแน่ใจหรือไม่ว่าต้องการอนุมัติการจองนี้?',
    type: 'success',
    onConfirm: async () => {
      try {
        await approvalStore.approve(id);
        ui.showAlert({ title: 'สำเร็จ', message: 'อนุมัติการจองแล้ว', type: 'success' });
      } catch (err: any) {
        ui.showAlert({ title: 'ผิดพลาด', message: err.response?.data?.detail || 'เกิดข้อผิดพลาด', type: 'error' });
      }
    }
  });
};

const openRejectModal = (id: number) => {
  selectedBookingId.value = id;
  actionNote.value = '';
  isRejectModalOpen.value = true;
};

const handleReject = async () => {
  if (!actionNote.value) {
    ui.showAlert({ title: 'คำเตือน', message: 'กรุณาระบุเหตุผลในการปฏิเสธ', type: 'warning' });
    return;
  }
  
  try {
    await approvalStore.reject(selectedBookingId.value!, actionNote.value);
    isRejectModalOpen.value = false;
    ui.showAlert({ title: 'สำเร็จ', message: 'ปฏิเสธการจองแล้ว', type: 'success' });
  } catch (err: any) {
    ui.showAlert({ title: 'ผิดพลาด', message: err.response?.data?.detail || 'เกิดข้อผิดพลาด', type: 'error' });
  }
};
</script>

<template>
  <MainLayout>
    <div class="animate-fade-in">
      <header class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <h1 class="text-4xl font-black text-base-content mb-2 flex items-center gap-4 tracking-tight">
            <Clock class="text-warning" :size="40" />
            รายการรออนุมัติ
          </h1>
          <p class="text-base-content/60 font-medium">ตรวจสอบและพิจารณาคำขอจองห้องประชุม (พบทั้งหมด <span class="text-primary font-black">{{ approvalStore.total }}</span> รายการ)</p>
        </div>

        <div class="flex flex-col sm:flex-row w-full md:w-auto gap-4">
          <!-- Search Input -->
          <div class="relative w-full sm:w-80 group">
            <Search :size="18" class="absolute left-4 top-1/2 -translate-y-1/2 text-base-content/30 group-focus-within:text-primary transition-colors" />
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="ค้นหาชื่อผู้จอง ห้องประชุม หรือหัวข้อ..." 
              class="input input-bordered w-full pl-12 h-12 rounded-2xl bg-base-100 border-base-content/10 focus:border-primary/30 transition-all font-medium shadow-sm"
            />
          </div>
          
          <!-- Page Size -->
          <div class="flex items-center gap-3 bg-base-200/50 px-4 rounded-2xl border border-base-content/5 h-12">
            <Filter :size="14" class="opacity-40" />
            <span class="text-[10px] font-black uppercase tracking-widest opacity-40">ROWS:</span>
            <select v-model="pageSize" class="select select-bordered select-xs font-black focus:outline-none bg-base-100 border-base-content/10">
              <option v-for="opt in pageSizeOptions" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>
        </div>
      </header>

      <div v-if="approvalStore.loading && approvalStore.pendingBookings.length === 0" class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div v-for="i in 4" :key="i" class="h-64 bg-base-100 rounded-3xl animate-pulse"></div>
      </div>

      <div v-else-if="approvalStore.pendingBookings.length > 0" class="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div v-for="booking in approvalStore.pendingBookings" :key="booking.id" 
          @click="openDetail(booking)"
          class="card bg-base-100 shadow-xl border border-base-content/5 hover:border-primary/30 transition-all cursor-pointer group">
          <div class="card-body p-6">
            <div class="flex justify-between items-start mb-4">
              <div class="flex items-center gap-4">
                <div class="w-14 h-14 bg-primary/10 rounded-2xl flex items-center justify-center text-primary font-bold text-xl">
                  {{ booking.snap_room_name.charAt(0) }}
                </div>
                <div>
                  <h3 class="font-bold text-xl">{{ booking.title }}</h3>
                  <p class="text-sm opacity-60">{{ booking.snap_room_name }} ({{ booking.snap_room_location }})</p>
                </div>
              </div>
              <div class="badge badge-warning font-bold">รอการอนุมัติ</div>
            </div>

            <div class="grid grid-cols-2 gap-4 py-4 bg-base-200/50 rounded-2xl px-6 mb-6">
              <div class="flex items-center gap-3">
                <Calendar :size="18" class="text-primary" />
                <div class="text-sm">
                  <div class="opacity-50 text-[10px] uppercase font-bold">วันที่</div>
                  <div class="font-semibold">{{ formatDate(booking.start_time) }}</div>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <Clock :size="18" class="text-primary" />
                <div class="text-sm">
                  <div class="opacity-50 text-[10px] uppercase font-bold">เวลา</div>
                  <div class="font-semibold">{{ formatTime(booking.start_time) }} - {{ formatTime(booking.end_time) }}</div>
                </div>
              </div>
            </div>

            <div class="flex items-center justify-between mb-6">
              <div class="flex items-center gap-2">
                <div class="avatar-group -space-x-3 rtl:space-x-reverse">
                  <div class="avatar placeholder">
                    <div class="bg-neutral text-neutral-content w-8 h-8 rounded-full flex items-center justify-center">
                      <span class="text-xs">U</span>
                    </div>
                  </div>
                </div>
                <div class="text-sm">
                  <span class="opacity-50">ผู้จอง:</span> 
                  <span class="font-bold ml-1">{{ booking.snap_user_name }}</span>
                </div>
              </div>
              <button @click="openDetail(booking)" class="btn btn-ghost btn-sm gap-2 text-primary">
                <Eye :size="16" /> ดูรายละเอียด
              </button>
            </div>

            <div class="card-actions grid grid-cols-2 gap-4 border-t border-base-content/5 pt-6" @click.stop>
              <button @click="openRejectModal(booking.id)" class="btn btn-outline btn-error gap-2">
                <XCircle :size="18" /> ปฏิเสธ
              </button>
              <button @click="handleApprove(booking.id)" class="btn btn-primary gap-2 shadow-lg shadow-primary/20">
                <CheckCircle :size="18" /> อนุมัติ
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination Footer -->
      <div v-if="approvalStore.total > 0" class="mt-10 p-6 bg-base-100 rounded-3xl border border-base-content/5 shadow-lg flex flex-col sm:flex-row justify-between items-center gap-4">
        <div class="text-xs font-black opacity-40 uppercase tracking-widest">
          Showing {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, approvalStore.total) }} of {{ approvalStore.total }} Requests
        </div>

        <div class="join shadow-sm border border-base-content/5 overflow-hidden">
          <button 
            class="join-item btn btn-sm px-6 bg-base-100 border-0 hover:bg-primary hover:text-white" 
            :disabled="currentPage === 1"
            @click="currentPage--; fetchPendingBookings()"
          >PREV</button>
          <button class="join-item btn btn-sm px-6 bg-base-100 border-0 font-black">PAGE {{ currentPage }}</button>
          <button 
            class="join-item btn btn-sm px-6 bg-base-100 border-0 hover:bg-primary hover:text-white" 
            :disabled="currentPage * pageSize >= approvalStore.total"
            @click="currentPage++; fetchPendingBookings()"
          >NEXT</button>
        </div>
      </div>

      <div v-if="approvalStore.total === 0 && !approvalStore.loading" class="card bg-base-100 py-32 text-center flex flex-col items-center shadow-xl rounded-[3rem] border border-base-content/5">
        <div class="w-24 h-24 bg-success/10 rounded-full flex items-center justify-center mb-8 text-success shadow-inner">
          <CheckCircle :size="50" />
        </div>
        <h3 class="text-3xl font-black text-base-content mb-3 uppercase tracking-tight">ไม่มีรายการรออนุมัติ</h3>
        <p class="text-base-content/50 max-w-xs mx-auto font-medium italic">"ขอบคุณที่ช่วยดูแลระบบ งานของคุณเสร็จสิ้นแล้วในขณะนี้!"</p>
        <button v-if="searchQuery" @click="searchQuery = ''" class="btn btn-ghost btn-sm mt-6 text-primary font-black uppercase tracking-widest">ล้างการค้นหา</button>
      </div>
    </div>

    <!-- Booking Detail Modal -->
    <BookingDetailModal 
      :is-open="isDetailModalOpen" 
      :booking="selectedBookingForDetail" 
      @close="isDetailModalOpen = false" 
    />

    <!-- Reject Modal -->
    <dialog ref="rejectDialogRef" class="modal" @close="handleRejectModalClose">
      <div class="modal-box border border-base-content/10 bg-base-100 shadow-2xl">
        <h3 class="font-bold text-2xl mb-4 text-error flex items-center gap-2">
          <MessageSquare :size="24" />
          ระบุเหตุผลการปฏิเสธ
        </h3>
        <p class="py-4 text-base-content/70">โปรดระบุเหตุผลเพื่อให้ผู้จองทราบและปรับปรุงแก้ไขในอนาคต</p>
        
        <textarea 
          v-model="actionNote" 
          class="textarea textarea-bordered w-full h-32 focus:textarea-error" 
          placeholder="เช่น ห้องถูกจองซ่อมบำรุง, ข้อมูลผู้เข้าร่วมไม่ชัดเจน..."
        ></textarea>

        <div class="modal-action gap-2">
          <button class="btn btn-ghost" @click="isRejectModalOpen = false">ยกเลิก</button>
          <button class="btn btn-error px-8" @click="handleReject">
            ยืนยันการปฏิเสธ
          </button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="isRejectModalOpen = false">
        <button>close</button>
      </form>
    </dialog>
  </MainLayout>
</template>
