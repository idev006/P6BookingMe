<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue';
import MainLayout from '../../components/layout/MainLayout.vue';
import api from '../../services/api';
import { useUIStore } from '../../stores/ui';
import { Users, UserX, Shield, MoreVertical, Search, CheckCircle, MessageSquare, Eye, X, Calendar, Clock, History, Mail, Briefcase, Activity } from 'lucide-vue-next';
import { formatDateTime, formatTime } from '../../utils/format';

const users = ref<any[]>([]);
const loading = ref(false);
const ui = useUIStore();
const searchQuery = ref('');
const isRejectModalOpen = ref(false);
const selectedUserId = ref<number | null>(null);
const rejectReason = ref('');
const rejectDialogRef = ref<HTMLDialogElement | null>(null);

const isAnonymizeModalOpen = ref(false);
const anonymizeConfirmText = ref('');
const userToAnonymize = ref<any>(null);
const anonymizeDialogRef = ref<HTMLDialogElement | null>(null);

const isDetailModalOpen = ref(false);
const selectedUserForDetail = ref<any | null>(null);
const detailDialogRef = ref<HTMLDialogElement | null>(null);
const pastBookings = ref<any[]>([]);
const futureBookings = ref<any[]>([]);
const bookingsLoading = ref(false);

watch(isRejectModalOpen, (newVal) => {
  if (newVal) rejectDialogRef.value?.showModal();
  else rejectDialogRef.value?.close();
});

watch(isAnonymizeModalOpen, (newVal) => {
  if (newVal) anonymizeDialogRef.value?.showModal();
  else anonymizeDialogRef.value?.close();
});

watch(isDetailModalOpen, (newVal) => {
  if (newVal) detailDialogRef.value?.showModal();
  else detailDialogRef.value?.close();
});

const handleRejectModalClose = () => { isRejectModalOpen.value = false; };
const handleAnonymizeModalClose = () => { isAnonymizeModalOpen.value = false; };
const handleDetailModalClose = () => { isDetailModalOpen.value = false; };

const openDetail = async (user: any) => {
  selectedUserForDetail.value = user;
  isDetailModalOpen.value = true;
  pastBookings.value = [];
  futureBookings.value = [];
  bookingsLoading.value = true;
  
  const now = new Date();
  
  try {
    const response = await api.get('/bookings/', { params: { user_id: user.id, limit: 50 } });
    const all = response.data.data.data;
    
    // Sort and Filter client-side for consistent behavior
    futureBookings.value = all
      .filter((b: any) => new Date(b.start_time) >= now && b.status !== 'cancelled')
      .sort((a: any, b: any) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
      .slice(0, 10);
      
    pastBookings.value = all
      .filter((b: any) => new Date(b.start_time) < now)
      .sort((a: any, b: any) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime())
      .slice(0, 10);
      
  } catch (err) {
    console.error('Failed to fetch user bookings', err);
  } finally {
    bookingsLoading.value = false;
  }
};

const currentPage = ref(1);
const pageSize = ref(10);
const totalUsers = ref(0);
const pageSizeOptions = [5, 10, 15, 25, 50];

const filteredUsers = computed(() => users.value);

const fetchUsers = async () => {
  loading.value = true;
  try {
    const skip = (currentPage.value - 1) * pageSize.value;
    const params = {
      skip,
      limit: pageSize.value,
      search: searchQuery.value || undefined,
      status: undefined // We can add status filter UI later if needed, but search is primary
    };
    const response = await api.get('/admin/users/', { params });
    users.value = response.data.data.data;
    totalUsers.value = response.data.data.total;
  } catch (err) {
    console.error('Failed to fetch users', err);
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
    fetchUsers();
  }, 500);
});

watch(pageSize, () => {
  currentPage.value = 1;
  fetchUsers();
});

onMounted(fetchUsers);

const handleApprove = async (id: number) => {
  ui.showConfirm({
    title: 'ยืนยันการอนุมัติ',
    message: 'คุณแน่ใจหรือไม่ว่าต้องการอนุมัติสมาชิกท่านนี้?',
    type: 'success',
    onConfirm: async () => {
      try {
        await api.post(`/admin/users/${id}/approve/`);
        ui.showAlert({ title: 'สำเร็จ', message: 'อนุมัติสมาชิกเรียบร้อยแล้ว', type: 'success' });
        fetchUsers();
      } catch (err: any) {
        ui.showAlert({ title: 'ผิดพลาด', message: err.response?.data?.detail || 'เกิดข้อผิดพลาด', type: 'error' });
      }
    }
  });
};

const openRejectModal = (id: number) => {
  selectedUserId.value = id;
  rejectReason.value = '';
  isRejectModalOpen.value = true;
};

const handleReject = async () => {
  if (!rejectReason.value) {
    ui.showAlert({ title: 'คำเตือน', message: 'กรุณาระบุเหตุผลการปฏิเสธ', type: 'warning' });
    return;
  }
  
  try {
    await api.post(`/admin/users/${selectedUserId.value}/reject/`, { reason: rejectReason.value });
    ui.showAlert({ title: 'สำเร็จ', message: 'ปฏิเสธสมาชิกเรียบร้อยแล้ว', type: 'success' });
    isRejectModalOpen.value = false;
    fetchUsers();
  } catch (err: any) {
    ui.showAlert({ title: 'ผิดพลาด', message: err.response?.data?.detail || 'เกิดข้อผิดพลาด', type: 'error' });
  }
};

const handleUpdateRole = async (id: number, role: string) => {
  ui.showConfirm({
    title: 'เปลี่ยนสิทธิ์ผู้ใช้งาน',
    message: `คุณแน่ใจหรือไม่ว่าต้องการเปลี่ยนสิทธิ์สมาชิกท่านนี้เป็น ${role.toUpperCase()}?`,
    type: 'warning',
    onConfirm: async () => {
      try {
        await api.post(`/admin/users/${id}/role/`, { role });
        ui.showAlert({ title: 'สำเร็จ', message: `ปรับเป็นสิทธิ์ ${role} แล้ว`, type: 'success' });
        fetchUsers();
      } catch (err: any) {
        ui.showAlert({ title: 'ผิดพลาด', message: err.response?.data?.detail || 'เกิดข้อผิดพลาด', type: 'error' });
      }
    }
  });
};

const handleUpdateStatus = async (id: number, status: string) => {
  ui.showConfirm({
    title: 'เปลี่ยนสถานะผู้ใช้งาน',
    message: `คุณแน่ใจหรือไม่ว่าต้องการเปลี่ยนสถานะสมาชิกท่านนี้เป็น ${status.toUpperCase()}?`,
    type: status === 'suspended' || status === 'rejected' ? 'error' : 'warning',
    onConfirm: async () => {
      try {
        await api.post(`/admin/users/${id}/status/`, { status });
        ui.showAlert({ title: 'สำเร็จ', message: `ปรับสถานะเป็น ${status} แล้ว`, type: 'success' });
        fetchUsers();
      } catch (err: any) {
        ui.showAlert({ title: 'ผิดพลาด', message: err.response?.data?.detail || 'เกิดข้อผิดพลาด', type: 'error' });
      }
    }
  });
};

const openAnonymizeModal = (user: any) => {
  userToAnonymize.value = user;
  anonymizeConfirmText.value = '';
  isAnonymizeModalOpen.value = true;
};

const handleAnonymize = async () => {
  if (anonymizeConfirmText.value !== userToAnonymize.value.full_name && anonymizeConfirmText.value !== 'CONFIRM') {
    ui.showAlert({ title: 'คำเตือน', message: 'ข้อความยืนยันไม่ถูกต้อง (พิมพ์ชื่อเต็ม หรือ CONFIRM)', type: 'warning' });
    return;
  }
  
  try {
    await api.post(`/admin/users/${userToAnonymize.value.id}/anonymize/`);
    ui.showAlert({ title: 'สำเร็จ', message: 'ทำลายข้อมูลส่วนบุคคล (PDPA) เรียบร้อยแล้ว', type: 'success' });
    isAnonymizeModalOpen.value = false;
    fetchUsers();
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
          <h1 class="text-3xl font-black text-base-content mb-2 flex items-center gap-3 tracking-tight">
            <Users class="text-primary" :size="32" />
            จัดการสมาชิก
          </h1>
          <p class="text-base-content/60 font-medium">ตรวจสอบ อนุมัติ และกำหนดสิทธิ์การใช้งานของสมาชิก</p>
        </div>

        <div class="flex flex-col sm:flex-row w-full md:w-auto gap-4">
          <!-- Search Input -->
          <div class="relative w-full sm:w-80 group">
            <Search :size="18" class="absolute left-4 top-1/2 -translate-y-1/2 text-base-content/30 group-focus-within:text-primary transition-colors" />
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="ค้นหาชื่อหรืออีเมลสมาชิก..." 
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
          <table class="table table-lg w-full">
            <thead>
              <tr class="bg-base-200/50">
                <th class="py-5 pl-8 font-black uppercase text-[10px] tracking-widest opacity-40">สมาชิก</th>
                <th class="py-5 font-black uppercase text-[10px] tracking-widest opacity-40">บทบาท (Role)</th>
                <th class="py-5 font-black uppercase text-[10px] tracking-widest opacity-40">สถานะ (Status)</th>
                <th class="py-5 font-black uppercase text-[10px] tracking-widest opacity-40 text-right">จัดการ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id" 
                  @click="openDetail(user)"
                  class="hover:bg-primary/5 transition-all cursor-pointer group border-b border-base-content/5">
                <td class="pl-8">
                  <div class="flex items-center gap-4">
                    <div class="avatar placeholder">
                      <div class="bg-primary/10 text-primary rounded-xl w-12 h-12 flex items-center justify-center font-black group-hover:bg-primary group-hover:text-white transition-all shadow-sm">
                        {{ user.full_name.charAt(0) }}
                      </div>
                    </div>
                    <div>
                      <div class="font-black text-lg group-hover:text-primary transition-colors tracking-tight">{{ user.full_name }}</div>
                      <div class="text-[10px] opacity-40 font-black uppercase tracking-widest">{{ user.email }} • ID: {{ user.employee_code || 'N/A' }}</div>
                    </div>
                  </div>
                </td>
                <td @click.stop>
                  <div class="dropdown dropdown-bottom">
                    <div tabindex="0" role="button" class="badge badge-outline cursor-pointer hover:badge-primary transition-all font-black uppercase tracking-widest p-3 text-[10px]">
                      {{ user.role }}
                    </div>
                    <ul tabindex="0" class="dropdown-content menu p-2 shadow-2xl bg-base-100 rounded-box w-52 border border-base-content/10 mt-2 z-10">
                      <li class="menu-title font-black uppercase text-[10px] opacity-30">Change Role</li>
                      <li><a @click="handleUpdateRole(user.id, 'member')" class="font-bold">Member</a></li>
                      <li><a @click="handleUpdateRole(user.id, 'approver')" class="font-bold">Approver</a></li>
                      <li><a @click="handleUpdateRole(user.id, 'admin')" class="font-bold">Admin</a></li>
                    </ul>
                  </div>
                </td>
                <td @click.stop>
                  <div v-if="user.status === 'pending'" class="flex items-center gap-2">
                    <span class="badge badge-warning font-black text-[10px] tracking-widest p-3">PENDING</span>
                    <div class="flex gap-1">
                      <button @click="handleApprove(user.id)" class="btn btn-xs btn-success gap-1 px-3 font-black">
                        <CheckCircle :size="12" /> อนุมัติ
                      </button>
                      <button @click="openRejectModal(user.id)" class="btn btn-xs btn-error gap-1 px-3 font-black">
                        <UserX :size="12" /> ปฏิเสธ
                      </button>
                    </div>
                  </div>
                  <div v-else class="dropdown dropdown-bottom">
                    <div tabindex="0" role="button" 
                      :class="['badge font-black uppercase cursor-pointer p-3 text-[10px] tracking-widest', user.status === 'active' ? 'badge-success' : 'badge-error', user.status === 'rejected' ? 'badge-neutral' : '']">
                      {{ user.status }}
                    </div>
                    <ul tabindex="0" class="dropdown-content menu p-2 shadow-2xl bg-base-100 rounded-box w-52 border border-base-content/10 mt-2 z-10">
                      <li class="menu-title font-black uppercase text-[10px] opacity-30">Change Status</li>
                      <li><a @click="handleUpdateStatus(user.id, 'active')" class="font-bold">Active</a></li>
                      <li><a @click="handleUpdateStatus(user.id, 'suspended')" class="font-bold">Suspend</a></li>
                      <li><a @click="handleUpdateStatus(user.id, 'rejected')" class="font-bold">Reject</a></li>
                    </ul>
                  </div>
                </td>
                <td class="text-right px-8" @click.stop>
                  <div class="flex justify-end gap-1">
                    <button @click="openDetail(user)" class="btn btn-ghost btn-sm btn-square text-primary tooltip" data-tip="ดูรายละเอียด">
                      <Eye :size="20" />
                    </button>
                    <div class="dropdown dropdown-end">
                      <div tabindex="0" role="button" class="btn btn-ghost btn-sm btn-square">
                        <MoreVertical :size="20" />
                      </div>
                      <ul tabindex="0" class="dropdown-content menu p-2 shadow-2xl bg-base-100 rounded-box w-52 border border-base-content/10 mt-2 z-10">
                        <li>
                          <a @click="openAnonymizeModal(user)" class="text-error hover:bg-error/10 hover:text-error font-black uppercase text-[10px] tracking-widest">
                            <UserX :size="16" /> Anonymize (PDPA)
                          </a>
                        </li>
                      </ul>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination Footer -->
        <div v-if="totalUsers > 0" class="p-6 bg-base-200/20 border-t border-base-content/5 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div class="text-xs font-black opacity-40 uppercase tracking-widest">
            Showing {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, totalUsers) }} of {{ totalUsers }} Users
          </div>

          <div class="join shadow-sm border border-base-content/5">
            <button 
              class="join-item btn btn-sm px-6 bg-base-100 border-0 hover:bg-primary hover:text-white" 
              :disabled="currentPage === 1"
              @click="currentPage--; fetchUsers()"
            >PREV</button>
            <button class="join-item btn btn-sm px-6 bg-base-100 border-0 font-black">PAGE {{ currentPage }}</button>
            <button 
              class="join-item btn btn-sm px-6 bg-base-100 border-0 hover:bg-primary hover:text-white" 
              :disabled="currentPage * pageSize >= totalUsers"
              @click="currentPage++; fetchUsers()"
            >NEXT</button>
          </div>
        </div>
      </div>
    </div>

    <!-- User Detail Long Modal (World Class UX) -->
    <dialog ref="detailDialogRef" class="modal" @close="handleDetailModalClose">
      <div v-if="selectedUserForDetail" class="modal-box w-11/12 max-w-2xl p-0 bg-base-100 shadow-2xl border border-base-content/10 overflow-hidden">
        <!-- Hero Header -->
        <div class="relative bg-gradient-to-br from-primary/20 via-base-100 to-secondary/10 p-12 border-b border-base-content/5">
          <div class="flex flex-col items-center text-center">
            <div class="avatar placeholder mb-6">
              <div class="bg-primary text-primary-content rounded-xl w-32 flex items-center justify-center shadow-2xl shadow-primary/20 ring-4 ring-white">
                <span class="text-5xl font-black">{{ selectedUserForDetail.full_name.charAt(0) }}</span>
              </div>
            </div>
            <h3 class="text-4xl font-black text-base-content tracking-tight leading-tight mb-2">{{ selectedUserForDetail.full_name }}</h3>
            <div class="flex items-center gap-3">
              <div :class="['badge font-black uppercase px-4 py-3 shadow-sm', selectedUserForDetail.status === 'active' ? 'badge-success' : 'badge-warning']">
                {{ selectedUserForDetail.status }}
              </div>
              <div class="badge badge-outline font-black uppercase px-4 py-3 opacity-60 border-base-content/20">{{ selectedUserForDetail.role }}</div>
            </div>
          </div>
          <button @click="isDetailModalOpen = false" class="btn btn-sm btn-circle btn-ghost absolute right-6 top-6">
            <X :size="20" />
          </button>
        </div>

        <div class="p-10 space-y-12 overflow-y-auto max-h-[60vh] premium-scroll">
          <!-- Account Details -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-base-200/30 p-6 rounded-3xl border border-base-content/5 space-y-1">
              <div class="text-[10px] opacity-40 uppercase font-black tracking-widest">Email Address</div>
              <div class="font-bold flex items-center gap-2 text-sm text-primary">
                <MessageSquare :size="14" /> {{ selectedUserForDetail.email }}
              </div>
            </div>
            <div class="bg-base-200/30 p-6 rounded-3xl border border-base-content/5 space-y-1">
              <div class="text-[10px] opacity-40 uppercase font-black tracking-widest">Employee Code</div>
              <div class="font-bold flex items-center gap-2 text-sm">
                <Shield :size="14" class="text-secondary" /> {{ selectedUserForDetail.employee_code || 'N/A' }}
              </div>
            </div>
          </div>

          <!-- Upcoming Bookings (Top 10) -->
          <div class="space-y-6">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-2xl bg-success/10 flex items-center justify-center text-success"><Calendar :size="20" /></div>
                <h4 class="text-xl font-black uppercase tracking-tight">รายการจองถัดไป (Top 10)</h4>
              </div>
              <div v-if="bookingsLoading" class="loading loading-spinner loading-sm text-primary"></div>
            </div>

            <div v-if="futureBookings.length > 0" class="space-y-3">
              <div v-for="booking in futureBookings" :key="booking.id" class="flex gap-6 p-6 bg-base-100 border border-base-content/5 hover:border-success/20 transition-all shadow-sm hover:shadow-md group">
                <div class="flex flex-col items-center justify-center min-w-[70px] border-r border-base-content/5 pr-6">
                  <div class="text-2xl font-black text-success">{{ new Date(booking.start_time).getDate() }}</div>
                  <div class="text-[10px] font-black uppercase opacity-40">{{ new Date(booking.start_time).toLocaleString('en-US', { month: 'short' }) }}</div>
                </div>
                <div class="flex-grow">
                  <div class="text-[10px] font-black opacity-30 uppercase tracking-widest mb-1">{{ booking.snap_room_name }}</div>
                  <h5 class="font-black text-lg group-hover:text-success transition-colors leading-tight">{{ booking.title }}</h5>
                  <div class="flex items-center gap-4 mt-2">
                    <div class="flex items-center gap-1.5 text-xs font-bold opacity-50"><Clock :size="12" /> {{ formatTime(booking.start_time) }} - {{ formatTime(booking.end_time) }}</div>
                  </div>
                </div>
                <div class="flex flex-col items-end justify-center">
                   <div :class="['badge badge-sm font-black text-[10px] tracking-widest px-3', booking.status === 'confirmed' ? 'badge-success' : 'badge-warning']">
                     {{ booking.status.toUpperCase() }}
                   </div>
                </div>
              </div>
            </div>
            <div v-else-if="!bookingsLoading" class="p-12 text-center bg-base-200/20 border border-dashed border-base-content/10">
              <div class="opacity-20 font-bold">ไม่มีรายการจองที่กำลังจะถึง</div>
            </div>
          </div>

          <!-- Past History (Top 10) -->
          <div class="space-y-6">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-neutral/10 flex items-center justify-center text-neutral"><History :size="20" /></div>
              <h4 class="text-xl font-black uppercase tracking-tight">ประวัติการจองที่ผ่านมา (Top 10)</h4>
            </div>

            <div v-if="pastBookings.length > 0" class="space-y-3">
              <div v-for="booking in pastBookings" :key="booking.id" class="flex gap-6 p-6 bg-base-200/20 border border-base-content/5 hover:border-neutral/20 transition-all group grayscale hover:grayscale-0 opacity-60 hover:opacity-100">
                <div class="flex flex-col items-center justify-center min-w-[70px] border-r border-base-content/5 pr-6">
                  <div class="text-xl font-black opacity-50">{{ new Date(booking.start_time).getDate() }}</div>
                  <div class="text-[10px] font-black uppercase opacity-30">{{ new Date(booking.start_time).toLocaleString('en-US', { month: 'short' }) }}</div>
                </div>
                <div class="flex-grow">
                  <div class="text-[10px] font-black opacity-30 uppercase tracking-widest mb-1">{{ booking.snap_room_name }}</div>
                  <h5 class="font-bold text-base leading-tight opacity-70 group-hover:opacity-100">{{ booking.title }}</h5>
                  <div class="text-[10px] font-bold opacity-40 mt-1">{{ formatTime(booking.start_time) }} - {{ formatTime(booking.end_time) }}</div>
                </div>
                <div class="flex flex-col items-end justify-center">
                   <div class="badge badge-ghost badge-sm font-black text-[10px] tracking-widest px-3 opacity-30">ARCHIVED</div>
                </div>
              </div>
            </div>
            <div v-else-if="!bookingsLoading" class="p-12 text-center bg-base-200/10 border border-dashed border-base-content/5">
              <div class="opacity-10 font-bold">ยังไม่มีประวัติการจอง</div>
            </div>
          </div>
        </div>

        <div class="p-8 bg-base-200/50 border-t border-base-content/5 flex justify-end">
           <button @click="isDetailModalOpen = false" class="btn btn-ghost px-12 font-black uppercase tracking-widest text-xs">ปิดหน้าต่าง</button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="isDetailModalOpen = false">
        <button>close</button>
      </form>
    </dialog>

    <!-- Reject Member Modal -->
    <dialog ref="rejectDialogRef" class="modal" @close="handleRejectModalClose">
      <div class="modal-box bg-base-100 border border-base-content/10 shadow-2xl">
        <h3 class="font-bold text-2xl mb-4 text-error flex items-center gap-2">
          <UserX :size="24" />
          ระบุเหตุผลการปฏิเสธสมาชิก
        </h3>
        <p class="py-4 text-base-content/70">โปรดระบุเหตุผลเพื่อให้ผู้สมัครทราบถึงสาเหตุที่ไม่สามารถเข้าใช้งานระบบได้</p>
        
        <textarea 
          v-model="rejectReason" 
          class="textarea textarea-bordered w-full h-32 focus:textarea-error" 
          placeholder="เช่น ข้อมูลรหัสพนักงานไม่ถูกต้อง, ไม่พบรายชื่อในหน่วยงานที่ระบุ..."
        ></textarea>

        <div class="modal-action gap-2">
          <button class="btn btn-ghost" @click="isRejectModalOpen = false">ยกเลิก</button>
          <button class="btn btn-error px-8 shadow-lg shadow-error/20" @click="handleReject">
            ยืนยันการปฏิเสธ
          </button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="isRejectModalOpen = false">
        <button>close</button>
      </form>
    </dialog>

    <!-- PDPA Anonymize Modal -->
    <dialog ref="anonymizeDialogRef" class="modal" @close="handleAnonymizeModalClose">
      <div class="modal-box bg-base-100 border-2 border-error/20 shadow-2xl">
        <h3 class="font-bold text-2xl mb-4 text-error flex items-center gap-2">
          <Shield :size="24" />
          ดำเนินการลบข้อมูล (PDPA Anonymization)
        </h3>
        
        <div class="alert alert-error bg-error/10 text-error-content border-error/20 mb-6 shadow-none">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6 text-error" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          <div>
            <h3 class="font-bold text-error">คำเตือน: การกระทำนี้ไม่สามารถย้อนกลับได้</h3>
            <div class="text-xs opacity-80 text-error">
              ข้อมูลส่วนบุคคลทั้งหมด (ชื่อ, อีเมล, เบอร์โทร, รหัสพนักงาน) ของ <b>{{ userToAnonymize?.full_name }}</b> จะถูกทำลายถาวร โดยจะเหลือเพียงประวัติการจองห้องที่ไม่ระบุตัวตน
            </div>
          </div>
        </div>
        
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text font-medium">เพื่อยืนยัน กรุณาพิมพ์ <b>CONFIRM</b> หรือพิมพ์ชื่อ <b>{{ userToAnonymize?.full_name }}</b></span>
          </label>
          <input 
            type="text" 
            v-model="anonymizeConfirmText" 
            class="input input-bordered border-error/30 focus:border-error focus:ring-1 focus:ring-error w-full" 
            placeholder="พิมพ์ข้อความยืนยัน..."
          />
        </div>

        <div class="modal-action gap-2">
          <button class="btn btn-ghost" @click="isAnonymizeModalOpen = false">ยกเลิก</button>
          <button 
            class="btn btn-error px-8 font-bold shadow-lg shadow-error/20" 
            @click="handleAnonymize"
            :disabled="anonymizeConfirmText !== userToAnonymize?.full_name && anonymizeConfirmText !== 'CONFIRM'"
          >
            ทำลายข้อมูลส่วนบุคคล
          </button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="isAnonymizeModalOpen = false">
        <button>close</button>
      </form>
    </dialog>
  </MainLayout>
</template>
