<script setup lang="ts">
import { onMounted, ref, watch, computed } from 'vue';
import MainLayout from '../../components/layout/MainLayout.vue';
import api from '../../services/api';
import { History, CheckCircle, XCircle, Calendar, Clock, User, Info, Eye, ChevronLeft, ChevronRight, Settings2 } from 'lucide-vue-next';
import { formatDateTime, formatDate, formatTime } from '../../utils/format';
import BookingDetailModal from '../../components/booking/BookingDetailModal.vue';

const history = ref<any[]>([]);
const loading = ref(false);
const total = ref(0);
const pageSize = ref(10);
const currentPage = ref(1);

const isDetailModalOpen = ref(false);
const selectedBookingForDetail = ref<any | null>(null);

const openDetail = (booking: any) => {
  selectedBookingForDetail.value = booking;
  isDetailModalOpen.value = true;
};

const fetchHistory = async () => {
  loading.value = true;
  try {
    const skip = (currentPage.value - 1) * pageSize.value;
    const response = await api.get(`/approvals/history/?limit=${pageSize.value}&skip=${skip}`);
    history.value = response.data.data.data;
    total.value = response.data.data.total;
  } catch (err) {
    console.error('Failed to fetch approval history', err);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchHistory);

watch([pageSize, currentPage], fetchHistory);

const totalPages = computed(() => Math.ceil(total.value / (pageSize.value || 1)));

const changePage = (page: number) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
};
</script>

<template>
  <MainLayout>
    <div class="animate-fade-in pb-20">
      <header class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <h1 class="text-4xl font-black text-base-content mb-2 flex items-center gap-4 tracking-tight">
            <History class="text-primary" :size="40" />
            ประวัติการอนุมัติ
          </h1>
          <p class="text-base-content/60 font-medium">รายการจองที่คุณเคยทำการพิจารณาอนุมัติหรือปฏิเสธ</p>
        </div>

        <!-- ROWS Selector -->
        <div class="flex items-center gap-3 bg-base-100 p-2 rounded-2xl border border-base-content/5 shadow-sm">
          <span class="text-[10px] font-black uppercase tracking-widest opacity-40 ml-2">Rows:</span>
          <select v-model="pageSize" class="select select-sm select-bordered bg-base-100 font-bold border-0 focus:ring-0">
            <option :value="5">5</option>
            <option :value="10">10</option>
            <option :value="15">15</option>
            <option :value="25">25</option>
            <option :value="50">50</option>
          </select>
        </div>
      </header>

      <div v-if="loading && history.length === 0" class="flex flex-col gap-4">
        <div v-for="i in 5" :key="i" class="h-24 bg-base-100 rounded-2xl animate-pulse border border-base-content/5"></div>
      </div>

      <div v-else-if="history.length > 0" class="grid grid-cols-1 gap-4">
        <div v-for="item in history" :key="item.id" 
          @click="openDetail(item.booking)"
          class="card bg-base-100 shadow-xl border border-base-content/5 hover:border-primary/40 hover:shadow-2xl hover:-translate-y-1 transition-all cursor-pointer group">
          <div class="card-body p-6 relative overflow-hidden">
            <div class="absolute right-0 top-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
              <Eye :size="24" class="text-primary" />
            </div>
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div class="flex items-center gap-4">
                <div :class="['w-12 h-12 rounded-xl flex items-center justify-center transition-transform group-hover:scale-110', item.action === 'approve' ? 'bg-success/10 text-success' : 'bg-error/10 text-error']">
                  <CheckCircle v-if="item.action === 'approve'" :size="24" />
                  <XCircle v-else :size="24" />
                </div>
                <div>
                  <h3 class="font-bold text-lg leading-tight group-hover:text-primary transition-colors">{{ item.booking?.title || 'N/A' }}</h3>
                  <div class="flex items-center gap-2 text-xs opacity-50 mt-1">
                    <User :size="12" /> {{ item.booking?.snap_user_name }} 
                    <span class="mx-1">•</span>
                    <Info :size="12" /> {{ item.booking?.snap_room_name }}
                  </div>
                </div>
              </div>

              <div class="flex flex-col items-end gap-1">
                <div :class="['badge font-bold uppercase tracking-widest px-4 py-3 shadow-sm', item.action === 'approve' ? 'badge-success' : 'badge-error']">
                  {{ item.action === 'approve' ? 'อนุมัติแล้ว' : 'ปฏิเสธ' }}
                </div>
                <div class="text-[10px] opacity-40 font-mono">
                  เมื่อ: {{ formatDate(item.actioned_at) }} {{ formatTime(item.actioned_at) }}
                </div>
              </div>
            </div>
            
            <div v-if="item.reason" class="mt-4 p-4 bg-base-200/50 rounded-2xl text-sm italic opacity-70 flex items-start gap-2 border border-base-content/5">
              <span class="font-bold shrink-0 text-primary">บันทึก:</span>
              <span>{{ item.reason }}</span>
            </div>
          </div>
        </div>

        <!-- Pagination Footer -->
        <div class="flex flex-col md:flex-row justify-between items-center mt-12 gap-6 bg-base-100 p-6 rounded-3xl border border-base-content/5 shadow-xl">
          <div class="text-sm font-medium opacity-50">
            แสดง <span class="font-black text-base-content">{{ history.length }}</span> จาก <span class="font-black text-base-content">{{ total }}</span> รายการ
          </div>
          
          <div class="join shadow-sm border border-base-content/5">
            <button 
              class="join-item btn btn-sm bg-base-100 border-0 hover:bg-primary hover:text-white transition-all disabled:opacity-20"
              :disabled="currentPage === 1"
              @click="changePage(currentPage - 1)">
              <ChevronLeft :size="18" />
            </button>
            <button class="join-item btn btn-sm bg-base-200 border-0 pointer-events-none font-black px-6">
              Page {{ currentPage }} / {{ totalPages }}
            </button>
            <button 
              class="join-item btn btn-sm bg-base-100 border-0 hover:bg-primary hover:text-white transition-all disabled:opacity-20"
              :disabled="currentPage === totalPages"
              @click="changePage(currentPage + 1)">
              <ChevronRight :size="18" />
            </button>
          </div>
        </div>
      </div>

      <div v-else class="card bg-base-100 py-32 text-center flex flex-col items-center shadow-xl border border-base-content/5">
        <div class="w-24 h-24 bg-base-200/50 rounded-full flex items-center justify-center mb-8 text-base-content/10">
          <History :size="48" />
        </div>
        <h3 class="text-3xl font-black text-base-content mb-3 tracking-tight">ยังไม่มีประวัติการพิจารณา</h3>
        <p class="text-base-content/40 font-medium max-w-xs mx-auto">รายการที่คุณอนุมัติหรือปฏิเสธจะถูกรวบรวมมาแสดงผลที่นี่เพื่อให้คุณตรวจสอบย้อนหลังได้</p>
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
