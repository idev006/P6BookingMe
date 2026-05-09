<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue';
import MainLayout from '../../components/layout/MainLayout.vue';
import auditService from '../../services/audit';
import { History, Search, Filter, Shield, Activity, Globe, Eye, Info, X } from 'lucide-vue-next';
import { formatDateTime } from '../../utils/format';

const logs = ref<any[]>([]);
const loading = ref(false);
const selectedLog = ref<any>(null);
const isModalOpen = ref(false);
const dialogRef = ref<HTMLDialogElement | null>(null);

watch(isModalOpen, (newVal) => {
  if (newVal) dialogRef.value?.showModal();
  else dialogRef.value?.close();
});

const handleModalClose = () => {
  isModalOpen.value = false;
};

const searchQuery = ref('');

// Pagination States
const currentPage = ref(1);
const pageSize = ref(15);
const totalLogs = ref(0);
const pageSizeOptions = [5, 10, 15, 25, 50];
const resourceFilter = ref('all');

const fetchLogs = async () => {
  loading.value = true;
  try {
    const skip = (currentPage.value - 1) * pageSize.value;
    const params = {
      skip,
      limit: pageSize.value,
      search: searchQuery.value || undefined,
      resource_type: resourceFilter.value !== 'all' ? resourceFilter.value : undefined
    };
    const response = await auditService.getLogs(params);
    logs.value = response.data.data.data;
    totalLogs.value = response.data.data.total;
  } catch (err) {
    console.error('Failed to fetch audit logs', err);
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
    fetchLogs();
  }, 500);
});

watch([resourceFilter, pageSize], () => {
  currentPage.value = 1;
  fetchLogs();
});

onMounted(fetchLogs);

const paginatedLogs = computed(() => logs.value);
const totalPages = computed(() => Math.ceil(totalLogs.value / pageSize.value));

const openDetails = (log: any) => {
  selectedLog.value = log;
  isModalOpen.value = true;
};

const getActionColor = (action: string) => {
  if (action.includes('create')) return 'text-success';
  if (action.includes('delete')) return 'text-error';
  if (action.includes('update')) return 'text-info';
  if (action.includes('approve')) return 'text-success font-bold';
  if (action.includes('reject')) return 'text-error font-bold';
  if (action.includes('reschedule')) return 'text-warning font-bold';
  return 'text-base-content';
};
</script>

<template>
  <MainLayout>
    <div class="animate-fade-in">
      <header class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <h1 class="text-3xl font-black text-base-content mb-2 flex items-center gap-3 tracking-tight">
            <History class="text-primary" :size="32" />
            Audit Logs
          </h1>
          <p class="text-base-content/60 font-medium">บันทึกกิจกรรมและประวัติการเปลี่ยนแปลงข้อมูลทั้งหมดในระบบ</p>
        </div>
        
        <div class="flex flex-col xl:flex-row w-full xl:w-auto gap-4">
          <!-- Resource Filter -->
          <div class="flex items-center gap-3 bg-base-200/50 px-4 rounded-2xl border border-base-content/5 h-12">
            <Filter :size="14" class="opacity-40" />
            <span class="text-[10px] font-black uppercase tracking-widest opacity-40">Resource</span>
            <select v-model="resourceFilter" class="select select-ghost select-xs font-black focus:outline-none bg-transparent">
              <option value="all">ทุกทรัพยากร</option>
              <option value="booking">จองห้องประชุม</option>
              <option value="user">สมาชิก</option>
              <option value="room">ห้องประชุม</option>
              <option value="config">ตั้งค่าระบบ</option>
            </select>
          </div>

          <!-- Search Input -->
          <div class="relative flex-grow sm:w-80 group">
            <Search :size="18" class="absolute left-4 top-1/2 -translate-y-1/2 text-base-content/30 group-focus-within:text-primary transition-colors" />
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="ค้นหากิจกรรม ผู้ดำเนินการ หรือทรัพยากร..." 
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

      <div class="card bg-base-100 shadow-2xl border border-base-content/5 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="table table-sm w-full">
            <thead>
              <tr class="bg-base-200/50">
                <th class="py-5 pl-8 font-black uppercase text-[10px] tracking-widest opacity-40">เวลา (Time)</th>
                <th class="py-5 font-black uppercase text-[10px] tracking-widest opacity-40">ผู้ดำเนินการ (User)</th>
                <th class="py-5 font-black uppercase text-[10px] tracking-widest opacity-40">กิจกรรม (Action)</th>
                <th class="py-5 font-black uppercase text-[10px] tracking-widest opacity-40">ข้อมูลที่เปลี่ยน</th>
                <th class="py-5 font-black uppercase text-[10px] tracking-widest opacity-40">IP Address</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in paginatedLogs" :key="log.id" 
                  @click="openDetails(log)"
                  class="hover:bg-primary/5 transition-all cursor-pointer border-b border-base-content/5 group">
                <td class="font-mono text-[10px] whitespace-nowrap opacity-60 pl-8">
                  {{ formatDateTime(log.created_at) }}
                </td>
                <td>
                  <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded bg-primary/10 flex items-center justify-center text-primary text-xs font-bold group-hover:bg-primary group-hover:text-white transition-all">
                      {{ log.user_name.charAt(0) }}
                    </div>
                    <div class="flex flex-col">
                      <span class="text-xs font-bold group-hover:text-primary transition-colors">{{ log.user_name }}</span>
                      <span class="text-[10px] opacity-40">ID #{{ log.user_id }}</span>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="flex flex-col gap-1">
                    <span :class="['text-[10px] font-bold uppercase tracking-wider', getActionColor(log.action)]">
                      {{ log.action.replace('.', ': ') }}
                    </span>
                    <div class="flex items-center gap-1.5 opacity-40">
                      <Activity :size="10" />
                      <span class="text-[9px] font-black uppercase">{{ log.resource_type }} #{{ log.resource_id }}</span>
                    </div>
                  </div>
                </td>
                <td class="max-w-xs" @click.stop>
                  <div class="flex items-center gap-2">
                    <button @click="openDetails(log)" class="text-left flex-grow">
                      <div class="text-[10px] bg-base-200 p-2 rounded-lg font-mono truncate hover:bg-base-300 transition-colors cursor-pointer flex items-center justify-between">
                        {{ log.new_value || log.old_value || '-' }}
                      </div>
                    </button>
                    <button @click="openDetails(log)" class="btn btn-ghost btn-xs btn-square text-primary">
                      <Eye :size="14" />
                    </button>
                  </div>
                </td>
                <td>
                  <div class="flex items-center gap-1 opacity-40">
                    <Globe :size="12" />
                    <span class="text-[10px] font-mono">{{ log.ip_address || 'local' }}</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination Footer -->
        <div v-if="totalLogs > 0" class="p-6 bg-base-200/20 border-t border-base-content/5 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div class="text-xs font-black opacity-40 uppercase tracking-widest">
            Showing {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, totalLogs) }} of {{ totalLogs }} Entries
          </div>

          <div class="join shadow-sm border border-base-content/5">
            <button 
              class="join-item btn btn-sm px-6 bg-base-100 border-0 hover:bg-primary hover:text-white" 
              :disabled="currentPage === 1"
              @click="currentPage--; fetchLogs()"
            >PREV</button>
            <button class="join-item btn btn-sm px-6 bg-base-100 border-0 font-black">PAGE {{ currentPage }}</button>
            <button 
              class="join-item btn btn-sm px-6 bg-base-100 border-0 hover:bg-primary hover:text-white" 
              :disabled="currentPage * pageSize >= totalLogs"
              @click="currentPage++; fetchLogs()"
            >NEXT</button>
          </div>
        </div>

        <div v-if="totalLogs === 0 && !loading" class="py-32 text-center flex flex-col items-center">
          <div class="w-20 h-20 bg-base-200 rounded-full flex items-center justify-center text-base-content/20 mb-6">
            <Search :size="40" />
          </div>
          <h3 class="text-2xl font-black opacity-20 uppercase tracking-widest">ไม่พบข้อมูลบันทึก</h3>
          <p class="text-sm opacity-30 mt-2">ลองเปลี่ยนคำค้นหาหรือตัวกรองเพื่อหาข้อมูลที่คุณต้องการ</p>
          <button @click="searchQuery = ''; resourceFilter = 'all'" class="btn btn-ghost btn-sm mt-4 text-primary font-black uppercase tracking-widest">ล้างการค้นหา</button>
        </div>
      </div>
    </div>

    <!-- Audit Log Detail Long Modal (World Class UX) -->
    <dialog ref="dialogRef" class="modal" @close="handleModalClose">
      <div v-if="selectedLog" class="modal-box w-11/12 max-w-3xl p-0 bg-base-100 shadow-2xl border border-base-content/10 overflow-hidden">
        <!-- Header -->
        <div class="relative bg-gradient-to-br from-primary/20 via-base-100 to-secondary/10 p-12 border-b border-base-content/5 text-center">
          <div class="flex flex-col items-center">
            <div class="w-20 h-20 rounded bg-primary flex items-center justify-center text-white shadow-2xl shadow-primary/30 mb-6">
              <Shield :size="40" />
            </div>
            <div class="badge badge-primary font-black uppercase text-[10px] tracking-widest mb-3 px-4 py-3">Security Intelligence</div>
            <h3 class="text-3xl font-black text-base-content tracking-tight leading-tight uppercase">{{ selectedLog.action.replace('.', ' ') }}</h3>
            <div class="flex items-center gap-2 mt-3 opacity-50 font-bold text-sm">
              <Clock :size="14" /> {{ formatDateTime(selectedLog.created_at) }}
            </div>
          </div>
          <button @click="isModalOpen = false" class="btn btn-sm btn-circle btn-ghost absolute right-6 top-6">
            <X :size="20" />
          </button>
        </div>

        <div class="p-10 space-y-12 overflow-y-auto max-h-[60vh] premium-scroll">
          <!-- Activity Fast Facts -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-base-200/50 p-6 border border-base-content/5">
              <div class="text-[10px] opacity-40 uppercase font-black tracking-widest mb-2">Performed By</div>
              <div class="font-bold flex items-center gap-2">
                <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary text-xs">{{ selectedLog.user_name.charAt(0) }}</div>
                {{ selectedLog.user_name }}
              </div>
            </div>
            <div class="bg-base-200/50 p-6 border border-base-content/5">
              <div class="text-[10px] opacity-40 uppercase font-black tracking-widest mb-2">Target Resource</div>
              <div class="font-bold text-sm">{{ selectedLog.resource_type }} <span class="opacity-30">#{{ selectedLog.resource_id }}</span></div>
            </div>
            <div class="bg-base-200/50 p-6 border border-base-content/5">
              <div class="text-[10px] opacity-40 uppercase font-black tracking-widest mb-2">Network Origin</div>
              <div class="font-bold text-sm flex items-center gap-2 italic">
                <Globe :size="14" class="opacity-30" /> {{ selectedLog.ip_address || 'Internal' }}
              </div>
            </div>
          </div>

          <!-- Configuration Diff (Long Format) -->
          <div class="space-y-8">
            <div v-if="selectedLog.old_value" class="space-y-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-base-300 flex items-center justify-center opacity-40"><History :size="20" /></div>
                <h4 class="text-xl font-black uppercase tracking-tight opacity-40">Old Configuration (BEFORE)</h4>
              </div>
              <div class="relative">
                 <pre class="bg-base-200/30 p-8 text-[11px] overflow-auto font-mono border border-base-content/5 opacity-60 italic">{{ JSON.stringify(selectedLog.old_value, null, 2) }}</pre>
                 <div class="absolute top-4 right-8 badge badge-outline badge-xs opacity-30">SNAPSHOT</div>
              </div>
            </div>

            <div v-if="selectedLog.new_value" class="space-y-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary"><Activity :size="20" /></div>
                <h4 class="text-xl font-black uppercase tracking-tight">New Configuration (AFTER)</h4>
              </div>
              <div class="relative">
                 <pre class="bg-primary/5 p-8 text-[11px] overflow-auto font-mono border border-primary/10 text-primary-content/80 font-bold shadow-inner">{{ JSON.stringify(selectedLog.new_value, null, 2) }}</pre>
                 <div class="absolute top-4 right-8 badge badge-primary badge-xs shadow-lg shadow-primary/20">CURRENT</div>
              </div>
            </div>
          </div>
        </div>

        <div class="p-8 bg-base-200/50 border-t border-base-content/5 flex justify-end">
           <button @click="isModalOpen = false" class="btn btn-ghost px-12 font-black uppercase tracking-widest text-xs">ปิดการตรวจสอบ</button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="isModalOpen = false">
        <button>close</button>
      </form>
    </dialog>
</MainLayout>
</template>
