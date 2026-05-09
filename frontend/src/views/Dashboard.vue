<script setup lang="ts">
import { onMounted, ref, watch, computed } from 'vue';
import MainLayout from '../components/layout/MainLayout.vue';
import { useAuthStore } from '../stores/auth';
import { useBookingStore } from '../stores/booking';
import { useUIStore } from '../stores/ui';
import { Calendar, Clock, CheckCircle2, Trash2, Eye, Pencil, Copy, Search, Filter, X } from 'lucide-vue-next';
import { formatTime, formatDate } from '../utils/format';
import BookingDetailModal from '../components/booking/BookingDetailModal.vue';
import { useRouter } from 'vue-router';

const auth = useAuthStore();
const bookingStore = useBookingStore();
const ui = useUIStore();
const router = useRouter();

const isDetailModalOpen = ref(false);
const selectedBookingForDetail = ref<any | null>(null);

// Search and Filter States
const searchQuery = ref('');
const statusFilter = ref('all');

// Pagination States
const currentPage = ref(1);
const pageSize = ref(10);
const pageSizeOptions = [5, 10, 15, 25, 50];

const getStatusClass = (status: string) => {
  switch (status) {
    case 'confirmed': return 'badge-success';
    case 'pending': return 'badge-warning';
    case 'rejected': return 'badge-error';
    case 'cancelled': return 'badge-neutral';
    default: return 'badge-ghost';
  }
};

const fetchMyBookings = async () => {
  const params = {
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value,
    search: searchQuery.value || undefined,
    status: statusFilter.value
  };
  await bookingStore.fetchMyBookings(params);
};

// Debounced search
let searchTimeout: any = null;
watch(searchQuery, () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    currentPage.value = 1;
    fetchMyBookings();
  }, 500);
});

watch([statusFilter, pageSize], () => {
  currentPage.value = 1;
  fetchMyBookings();
});

onMounted(fetchMyBookings);

const paginatedBookings = computed(() => bookingStore.myBookings);
const totalBookings = computed(() => bookingStore.total);
const totalPages = computed(() => Math.ceil(totalBookings.value / pageSize.value));

const openDetail = (booking: any) => {
  selectedBookingForDetail.value = booking;
  isDetailModalOpen.value = true;
};

const handleEdit = (booking: any) => {
  router.push({
    name: 'Booking',
    params: { id: booking.room_id },
    query: { edit: booking.id }
  });
};

const handleDuplicate = (booking: any) => {
  router.push({
    name: 'Booking',
    params: { id: booking.room_id },
    query: { duplicate: booking.id }
  });
};

const handleCancel = (id: number) => {
  ui.showConfirm({
    title: 'ยืนยันการยกเลิก',
    message: 'คุณแน่ใจหรือไม่ว่าต้องการยกเลิกการจองนี้? การดำเนินการนี้ไม่สามารถเรียกคืนได้',
    type: 'warning',
    onConfirm: async () => {
      try {
        await bookingStore.cancelBooking(id);
        ui.showAlert({
          title: 'สำเร็จ',
          message: 'ยกเลิกการจองเรียบร้อยแล้ว',
          type: 'success'
        });
      } catch (err: any) {
        ui.showAlert({
          title: 'เกิดข้อผิดพลาด',
          message: err.response?.data?.detail || 'ไม่สามารถยกเลิกการจองได้',
          type: 'error'
        });
      }
    }
  });
};
</script>

<template>
  <MainLayout>
    <div class="animate-fade-in">
      <header class="mb-8 flex justify-between items-end">
        <div>
          <h1 class="text-3xl font-bold text-base-content mb-2">ยินดีต้อนรับ, {{ auth.user?.full_name }}</h1>
          <p class="text-base-content/60">ภาพรวมการใช้งานและสถานะการจองห้องประชุมของคุณ</p>
        </div>
        <router-link to="/rooms" class="btn btn-primary shadow-lg shadow-primary/20">จองห้องใหม่</router-link>
      </header>

      <!-- Stats Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <div class="stats shadow bg-base-100 border border-base-content/5">
          <div class="stat">
            <div class="stat-figure text-primary">
              <Calendar :size="32" />
            </div>
            <div class="stat-title">การจองทั้งหมด</div>
            <div class="stat-value text-primary">{{ bookingStore.myBookings.length }}</div>
            <div class="stat-desc">ครั้งนี้และที่ผ่านมา</div>
          </div>
        </div>
        
        <div class="stats shadow bg-base-100 border border-base-content/5">
          <div class="stat">
            <div class="stat-figure text-success">
              <CheckCircle2 :size="32" />
            </div>
            <div class="stat-title">อนุมัติแล้ว</div>
            <div class="stat-value text-success">
              {{ bookingStore.myBookings.filter(b => b.status === 'confirmed').length }}
            </div>
            <div class="stat-desc">พร้อมใช้งาน</div>
          </div>
        </div>

        <div class="stats shadow bg-base-100 border border-base-content/5">
          <div class="stat">
            <div class="stat-figure text-warning">
              <Clock :size="32" />
            </div>
            <div class="stat-title">รออนุมัติ</div>
            <div class="stat-value text-warning">
              {{ bookingStore.myBookings.filter(b => b.status === 'pending').length }}
            </div>
            <div class="stat-desc">อยู่ระหว่างการพิจารณา</div>
          </div>
        </div>
      </div>

      <!-- Bookings List -->
      <div class="card bg-base-100 shadow-xl border border-base-content/5 overflow-hidden">
        <div class="card-body p-0">
          <div class="p-6 border-b border-base-content/10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-base-100">
            <h2 class="card-title text-xl font-black uppercase tracking-tight">รายการจองล่าสุด</h2>
            
            <div class="flex flex-col sm:flex-row w-full md:w-auto gap-3">
              <!-- Search Input -->
              <div class="relative w-full sm:w-64 group">
                <Search :size="16" class="absolute left-4 top-1/2 -translate-y-1/2 text-base-content/30 group-focus-within:text-primary transition-colors" />
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="ค้นหาหัวข้อหรือชื่อห้อง..." 
                  class="input input-sm input-bordered w-full h-10 pl-11 rounded-xl bg-base-200/50 border-transparent focus:border-primary/30 focus:bg-base-100 transition-all font-medium"
                />
              </div>

              <!-- Status Filter Tabs (DaisyUI style) -->
              <div class="join bg-base-200/50 p-1 rounded-xl">
                <button 
                  v-for="status in ['all', 'pending', 'confirmed', 'rejected']" 
                  :key="status"
                  @click="statusFilter = status"
                  :class="['btn btn-xs join-item h-8 px-4 border-0 rounded-lg transition-all', statusFilter === status ? 'bg-base-100 shadow-sm text-primary font-bold' : 'bg-transparent hover:bg-base-100/50 opacity-50 font-bold uppercase text-[10px]']"
                >
                  {{ status === 'all' ? 'ทั้งหมด' : status }}
                </button>
              </div>
            </div>
          </div>
          
          <div class="overflow-x-auto">
            <table class="table table-zebra w-full">
              <thead>
                <tr class="bg-base-200/20">
                  <th class="py-4 font-black uppercase text-[10px] tracking-widest opacity-40">ห้องประชุม</th>
                  <th class="py-4 font-black uppercase text-[10px] tracking-widest opacity-40">หัวข้อ</th>
                  <th class="py-4 font-black uppercase text-[10px] tracking-widest opacity-40">วัน-เวลา</th>
                  <th class="py-4 font-black uppercase text-[10px] tracking-widest opacity-40">สถานะ</th>
                  <th class="py-4 font-black uppercase text-[10px] tracking-widest opacity-40 text-right">จัดการ</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="booking in paginatedBookings" :key="booking.id" 
                    @click="openDetail(booking)"
                    class="hover:bg-primary/5 transition-colors cursor-pointer group">
                  <td>
                    <div class="flex items-center gap-3">
                      <div class="avatar placeholder">
                        <div class="bg-primary text-primary-content rounded-lg w-12 h-12 flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg shadow-primary/10">
                          <span class="font-black leading-none">{{ booking.snap_room_name.charAt(0) }}</span>
                        </div>
                      </div>
                      <div>
                        <div class="font-bold group-hover:text-primary transition-colors text-sm">{{ booking.snap_room_name }}</div>
                        <div class="text-[10px] opacity-50 font-black uppercase tracking-tighter">{{ booking.snap_room_location }}</div>
                      </div>
                    </div>
                  </td>
                  <td class="font-medium text-sm max-w-xs truncate">{{ booking.title }}</td>
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
                    <div :class="['badge badge-sm font-black uppercase py-3 px-4 text-[10px] tracking-tighter shadow-sm', getStatusClass(booking.status)]">
                      {{ booking.status }}
                    </div>
                  </td>
                  <td class="text-right px-4" @click.stop>
                    <div class="flex justify-end gap-1">
                      <button @click="openDetail(booking)" class="btn btn-ghost btn-sm btn-square text-primary tooltip" data-tip="ดูรายละเอียด">
                        <Eye :size="18" />
                      </button>
                      <button 
                        v-if="booking.status === 'pending' || booking.status === 'confirmed'" 
                        @click="handleEdit(booking)" 
                        class="btn btn-ghost btn-sm btn-square text-info hover:bg-info/10 tooltip"
                        data-tip="แก้ไขการจอง"
                      >
                        <Pencil :size="18" />
                      </button>
                      <button 
                        @click="handleDuplicate(booking)" 
                        class="btn btn-ghost btn-sm btn-square text-success hover:bg-success/10 tooltip"
                        data-tip="จองซ้ำ (Duplicate)"
                      >
                        <Copy :size="18" />
                      </button>
                      <button 
                        v-if="booking.status === 'pending' || booking.status === 'confirmed'" 
                        @click="handleCancel(booking.id)" 
                        class="btn btn-ghost btn-sm btn-square text-error hover:bg-error/10 tooltip"
                        data-tip="ยกเลิกการจอง"
                      >
                        <Trash2 :size="18" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination Footer -->
          <div v-if="totalBookings > 0" class="p-4 bg-base-200/30 border-t border-base-content/5 flex flex-col sm:flex-row justify-between items-center gap-4">
            <div class="flex items-center gap-4">
              <div class="flex items-center gap-2">
                <span class="text-[10px] font-black uppercase tracking-widest opacity-40">ROWS:</span>
                <select v-model="pageSize" class="select select-bordered select-xs rounded-lg font-bold bg-base-100 focus:outline-none border-base-content/10">
                  <option v-for="opt in pageSizeOptions" :key="opt" :value="opt">{{ opt }}</option>
                </select>
              </div>
              <span class="text-xs opacity-50 font-black uppercase tracking-widest">
                Showing {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, totalBookings) }} of {{ totalBookings }}
              </span>
            </div>

            <div class="join shadow-sm border border-base-content/5 overflow-hidden">
              <button 
                class="join-item btn btn-xs px-4 bg-base-100 border-0 hover:bg-primary hover:text-white" 
                :disabled="currentPage === 1"
                @click="currentPage--; fetchMyBookings()"
              >PREV</button>
              <button class="join-item btn btn-xs px-4 bg-base-100 border-0 font-black">PAGE {{ currentPage }}</button>
              <button 
                class="join-item btn btn-xs px-4 bg-base-100 border-0 hover:bg-primary hover:text-white" 
                :disabled="currentPage * pageSize >= totalBookings"
                @click="currentPage++; fetchMyBookings()"
              >NEXT</button>
            </div>
          </div>

          <!-- Empty State (No Search Results) -->
          <div v-if="totalBookings === 0 && (searchQuery || statusFilter !== 'all') && !bookingStore.loading" class="py-20 text-center flex flex-col items-center border-t border-base-content/5">
            <div class="w-16 h-16 bg-base-200 rounded-full flex items-center justify-center text-base-content/20 mb-4">
              <Search :size="32" />
            </div>
            <h3 class="text-xl font-black opacity-20 uppercase tracking-widest">ไม่พบรายการที่ตรงกับการค้นหา</h3>
            <p class="text-sm opacity-30 mt-1">ลองเปลี่ยนคำค้นหาหรือตัวกรองสถานะ</p>
            <button @click="searchQuery = ''; statusFilter = 'all'" class="btn btn-ghost btn-sm mt-4 text-primary font-black uppercase tracking-widest">ล้างการค้นหา</button>
          </div>

          <!-- Empty State (No Bookings at all) -->
          <div v-if="totalBookings === 0 && !searchQuery && statusFilter === 'all' && !bookingStore.loading" class="py-32 text-center flex flex-col items-center border-t border-base-content/5">
            <div class="w-20 h-20 bg-primary/5 rounded-full flex items-center justify-center text-primary/20 mb-6">
              <Calendar :size="40" />
            </div>
            <h3 class="text-2xl font-black opacity-20 uppercase tracking-widest">ยังไม่มีรายการจอง</h3>
            <p class="text-sm opacity-30 mt-2 font-medium">เริ่มต้นจองห้องประชุมห้องแรกของคุณได้ที่เมนู "จองห้องประชุม"</p>
            <router-link to="/rooms" class="btn btn-primary btn-md rounded-2xl px-10 mt-8 shadow-xl shadow-primary/20 font-black">จองห้องประชุมทันที</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Booking Detail Modal -->
    <BookingDetailModal 
      :is-open="isDetailModalOpen" 
      :booking="selectedBookingForDetail" 
      @close="isDetailModalOpen = false" 
    />
  </MainLayout>
</template>
