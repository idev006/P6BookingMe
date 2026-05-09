<script setup lang="ts">
import { onMounted, ref } from 'vue';
import MainLayout from '../../components/layout/MainLayout.vue';
import api from '../../services/api';
import { 
  BarChart3, 
  CalendarCheck, 
  TrendingUp, 
  CheckCircle2, 
  DoorOpen, 
  Download,
  CalendarDays,
  FileSpreadsheet,
  Eye,
  Activity,
  ArrowRight
} from 'lucide-vue-next';
import BookingDetailModal from '../../components/booking/BookingDetailModal.vue';
import { formatDate, formatTime } from '../../utils/format';

const stats = ref<any>(null);
const frequentRooms = ref<any[]>([]);
const usageTrends = ref<any[]>([]);
const recentBookings = ref<any[]>([]);
const loading = ref(false);

const isDetailModalOpen = ref(false);
const selectedBookingForDetail = ref<any | null>(null);

const fetchData = async () => {
  loading.value = true;
  try {
    const [summaryRes, roomsRes, trendsRes, recentRes] = await Promise.all([
      api.get('/admin/reporting/summary'),
      api.get('/admin/reporting/frequent-rooms'),
      api.get('/admin/reporting/usage-trends'),
      api.get('/admin/bookings?limit=5') // Fetch recent 5
    ]);
    
    stats.value = summaryRes.data.data;
    frequentRooms.value = roomsRes.data.data;
    usageTrends.value = trendsRes.data.data;
    recentBookings.value = recentRes.data.data.data;
  } catch (err) {
    console.error('Failed to fetch dashboard data', err);
  } finally {
    loading.value = false;
  }
};

const openDetail = (booking: any) => {
  selectedBookingForDetail.value = booking;
  isDetailModalOpen.value = true;
};

const handleExport = async () => {
  // ... existing code ...
  try {
    const response = await api.get('/admin/reporting/export/bookings', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `bookings_export_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (err) {
    console.error('Export failed', err);
  }
};

const getMaxTrendValue = () => {
  if (usageTrends.value.length === 0) return 1;
  return Math.max(...usageTrends.value.map(t => t.count), 5);
};

onMounted(fetchData);
</script>

<template>
  <MainLayout>
    <div class="animate-fade-in space-y-10">
      <header class="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 class="text-4xl font-black text-base-content tracking-tight mb-2 flex items-center gap-4">
            <BarChart3 class="text-primary" :size="40" />
            Admin Insights
          </h1>
          <p class="text-base-content/60 text-lg">สถิติและการวิเคราะห์การใช้งานระบบจองห้องประชุม</p>
        </div>
        
        <button @click="handleExport" class="btn btn-primary gap-2 shadow-lg shadow-primary/20">
          <FileSpreadsheet :size="18" />
          ส่งออกรายงานการจอง (.csv)
        </button>
      </header>

      <!-- Stats Cards -->
      <div v-if="stats" class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <router-link to="/admin/bookings" class="card bg-base-100 shadow-xl border border-base-content/5 overflow-hidden group hover:border-primary/40 transition-all">
          <div class="card-body p-8 flex-row items-center gap-6">
            <div class="w-16 h-16 rounded bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-white transition-all">
              <CalendarCheck :size="28" />
            </div>
            <div>
              <div class="text-4xl font-black">{{ stats.today_total }}</div>
              <div class="text-sm uppercase font-bold tracking-widest opacity-40">จองวันนี้</div>
            </div>
          </div>
        </router-link>

        <router-link to="/admin/approvals" class="card bg-base-100 shadow-xl border border-base-content/5 overflow-hidden group hover:border-warning/40 transition-all">
          <div class="card-body p-8 flex-row items-center gap-6">
            <div class="w-16 h-16 rounded bg-warning/10 flex items-center justify-center text-warning group-hover:bg-warning group-hover:text-white transition-all">
              <TrendingUp :size="28" />
            </div>
            <div>
              <div class="text-4xl font-black text-warning">{{ stats.pending_approval }}</div>
              <div class="text-sm uppercase font-bold tracking-widest opacity-40">รออนุมัติ</div>
            </div>
          </div>
        </router-link>

        <div class="card bg-base-100 shadow-xl border border-base-content/5 overflow-hidden group">
          <div class="card-body p-8 flex-row items-center gap-6">
            <div class="w-16 h-16 rounded bg-success/10 flex items-center justify-center text-success transition-all">
              <CheckCircle2 :size="28" />
            </div>
            <div>
              <div class="text-4xl font-black text-success">{{ stats.today_confirmed }}</div>
              <div class="text-sm uppercase font-bold tracking-widest opacity-40">ยืนยันแล้ววันนี้</div>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-3 gap-10">
        <!-- Usage Trends Chart -->
        <div class="card bg-base-100 shadow-xl border border-base-content/5 xl:col-span-2">
          <div class="card-body p-8">
            <div class="flex items-center justify-between mb-8">
              <h3 class="card-title text-xl font-bold flex items-center gap-2">
                <CalendarDays class="text-primary" :size="20" />
                แนวโน้มการจอง (7 วันล่าสุด)
              </h3>
            </div>
            
            <div class="flex items-end justify-between h-56 gap-3 px-4 pb-2 border-b border-base-content/10">
              <div v-for="day in usageTrends" :key="day.date" 
                class="group relative flex-grow flex flex-col items-center">
                <div class="w-full bg-primary/20 rounded-t-xl transition-all duration-500 hover:bg-primary"
                  :style="{ height: `${(day.count / getMaxTrendValue()) * 100}%`, minHeight: '8px' }">
                </div>
                <!-- Tooltip -->
                <div class="absolute -top-10 left-1/2 -translate-x-1/2 bg-neutral text-neutral-content text-xs px-3 py-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-xl z-20">
                  {{ day.count }} การจอง
                </div>
                <span class="text-[10px] opacity-40 mt-3 font-bold uppercase">{{ new Date(day.date).toLocaleDateString('th-TH', { weekday: 'short' }) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Top Rooms -->
        <div class="card bg-base-100 shadow-xl border border-base-content/5">
          <div class="card-body p-8">
            <h3 class="card-title text-xl font-bold mb-8 flex items-center gap-2">
              <DoorOpen class="text-secondary" :size="20" />
              ห้องที่ถูกจองบ่อยที่สุด
            </h3>
            <div class="space-y-6">
              <div v-for="(room, index) in frequentRooms" :key="room.name" class="space-y-3">
                <div class="flex justify-between items-center">
                  <div class="flex items-center gap-3">
                    <span class="w-6 h-6 flex items-center justify-center bg-base-200 rounded-lg text-[10px] font-bold">{{ index + 1 }}</span>
                    <span class="font-bold text-base-content/80">{{ room.name }}</span>
                  </div>
                  <span class="badge badge-ghost font-mono">{{ room.value }} ครั้ง</span>
                </div>
                <div class="w-full h-2 bg-base-200 rounded-full overflow-hidden">
                  <div class="h-full bg-gradient-to-r from-primary to-secondary rounded-full transition-all duration-1000" 
                    :style="{ width: `${(room.value / (frequentRooms[0]?.value || 1)) * 100}%` }">
                  </div>
                </div>
              </div>
              
              <div v-if="frequentRooms.length === 0" class="py-10 text-center opacity-30 italic">
                ยังไม่มีข้อมูลการจอง
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity (Consistency Requirement) -->
      <div class="card bg-base-100 shadow-xl border border-base-content/5 overflow-hidden">
        <div class="card-body p-0">
          <div class="p-8 border-b border-base-content/5 flex justify-between items-center">
            <h2 class="card-title text-2xl font-black flex items-center gap-3">
              <Activity class="text-primary" />
              กิจกรรมการจองล่าสุด
            </h2>
            <router-link to="/admin/bookings" class="btn btn-ghost btn-sm gap-2 opacity-50 hover:opacity-100">
              ดูทั้งหมด <ArrowRight :size="16" />
            </router-link>
          </div>
          
          <div class="overflow-x-auto">
            <table class="table table-lg w-full">
              <thead>
                <tr class="bg-base-200/50">
                  <th>รายการ</th>
                  <th>ผู้จอง</th>
                  <th>วัน-เวลา</th>
                  <th>สถานะ</th>
                  <th class="text-right px-8">รายละเอียด</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="booking in recentBookings" :key="booking.id" 
                  @click="openDetail(booking)"
                  class="hover:bg-primary/5 transition-all cursor-pointer group border-b border-base-content/5">
                  <td>
                    <div class="flex items-center gap-4">
                      <div class="w-10 h-10 bg-primary/10 rounded-xl flex items-center justify-center text-primary font-bold group-hover:bg-primary group-hover:text-white transition-all">
                        {{ booking.snap_room_name.charAt(0) }}
                      </div>
                      <div class="font-bold group-hover:text-primary transition-colors">{{ booking.title }}</div>
                    </div>
                  </td>
                  <td>
                    <span class="text-sm font-medium opacity-70">{{ booking.snap_user_name }}</span>
                  </td>
                  <td>
                    <div class="flex flex-col text-xs font-bold">
                      <span>{{ formatDate(booking.start_time) }}</span>
                      <span class="opacity-40">{{ formatTime(booking.start_time) }} - {{ formatTime(booking.end_time) }}</span>
                    </div>
                  </td>
                  <td>
                    <div :class="['badge badge-sm font-bold uppercase p-3', 
                      booking.status === 'confirmed' ? 'badge-success' : 
                      booking.status === 'pending' ? 'badge-warning' : 'badge-neutral']">
                      {{ booking.status }}
                    </div>
                  </td>
                  <td class="text-right px-8">
                    <button @click.stop="openDetail(booking)" class="btn btn-ghost btn-sm btn-square text-primary">
                      <Eye :size="18" />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
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
