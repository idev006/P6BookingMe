<script setup lang="ts">
import { onMounted, ref, reactive, watch, computed } from 'vue';
import MainLayout from '../../components/layout/MainLayout.vue';
import api from '../../services/api';
import { useRoomStore } from '../../stores/room';
import roomAdminService from '../../services/roomAdmin';
import { useUIStore } from '../../stores/ui';
import { Plus, Edit2, Trash2, MapPin, Users, Check, X, Camera, Eye, Calendar, Clock, Info, History, Search, Filter } from 'lucide-vue-next';
import { formatDate, formatTime } from '../../utils/format';

const roomStore = useRoomStore();
const ui = useUIStore();

const isModalOpen = ref(false);
const isImageModalOpen = ref(false);
const isDetailModalOpen = ref(false);
const isEditing = ref(false);
const currentRoomId = ref<number | null>(null);
const currentRoom = ref<any>(null);
const uploadLoading = ref(false);
const pastBookings = ref<any[]>([]);
const futureBookings = ref<any[]>([]);
const bookingsLoading = ref(false);
const searchQuery = ref('');
const statusFilter = ref('all');

// Pagination States
const currentPage = ref(1);
const pageSize = ref(10);
const pageSizeOptions = [5, 10, 15, 25, 50];

const fetchRooms = async () => {
  const params = {
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value,
    search: searchQuery.value || undefined,
    status: statusFilter.value
  };
  await roomStore.fetchRooms(params, true);
};

// Debounced search
let searchTimeout: any = null;
watch(searchQuery, () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    currentPage.value = 1;
    fetchRooms();
  }, 500);
});

watch([statusFilter, pageSize], () => {
  currentPage.value = 1;
  fetchRooms();
});

const paginatedRooms = computed(() => roomStore.rooms);
const totalRooms = computed(() => roomStore.total);
const totalPages = computed(() => Math.ceil(totalRooms.value / pageSize.value));

const modalDialogRef = ref<HTMLDialogElement | null>(null);
const imageDialogRef = ref<HTMLDialogElement | null>(null);
const detailDialogRef = ref<HTMLDialogElement | null>(null);

watch(isModalOpen, (newVal) => {
  if (newVal) modalDialogRef.value?.showModal();
  else modalDialogRef.value?.close();
});

watch(isImageModalOpen, (newVal) => {
  if (newVal) imageDialogRef.value?.showModal();
  else imageDialogRef.value?.close();
});

watch(isDetailModalOpen, (newVal) => {
  if (newVal) detailDialogRef.value?.showModal();
  else detailDialogRef.value?.close();
});

const handleModalClose = () => { isModalOpen.value = false; };
const handleImageModalClose = () => { isImageModalOpen.value = false; };
const handleDetailModalClose = () => { isDetailModalOpen.value = false; };

const roomForm = reactive({
  name: '',
  capacity: 10,
  building: '',
  floor: '',
  location: '',
  description: '',
  status: 'active'
});

onMounted(() => {
  fetchRooms();
});

const openAddModal = () => {
  isEditing.value = false;
  currentRoomId.value = null;
  Object.assign(roomForm, {
    name: '',
    capacity: 10,
    building: '',
    floor: '',
    location: '',
    description: '',
    status: 'active'
  });
  isModalOpen.value = true;
};

const openEditModal = (room: any) => {
  isEditing.value = true;
  currentRoomId.value = room.id;
  Object.assign(roomForm, {
    name: room.name,
    capacity: room.capacity,
    building: room.building,
    floor: room.floor,
    location: room.location,
    description: room.description,
    status: room.status
  });
  isModalOpen.value = true;
};

const openRoomDetail = async (room: any) => {
  currentRoom.value = room;
  isDetailModalOpen.value = true;
  pastBookings.value = [];
  futureBookings.value = [];
  bookingsLoading.value = true;
  
  const now = new Date().toISOString();
  
  try {
    const [futureRes, pastRes] = await Promise.all([
      api.get('/bookings', { params: { 
        room_id: room.id, 
        status: 'confirmed', 
        start_time_after: now,
        limit: 10,
        sort: 'start_time',
        order: 'asc'
      }}),
      api.get('/bookings', { params: { 
        room_id: room.id, 
        status: 'confirmed', 
        end_time_before: now,
        limit: 10,
        sort: 'start_time',
        order: 'desc'
      }})
    ]);
    
    futureBookings.value = futureRes.data.data.data;
    pastBookings.value = pastRes.data.data.data;
  } catch (err) {
    console.error('Failed to fetch room bookings', err);
    // Fallback if specific filters not supported, fetch all and filter client side
    try {
      const allRes = await api.get('/bookings', { params: { room_id: room.id, status: 'confirmed', limit: 50 } });
      const all = allRes.data.data.data;
      futureBookings.value = all.filter((b: any) => new Date(b.start_time) >= new Date()).slice(0, 10);
      pastBookings.value = all.filter((b: any) => new Date(b.start_time) < new Date()).sort((a:any, b:any) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime()).slice(0, 10);
    } catch (e) {
      console.error('Final fallback failed', e);
    }
  } finally {
    bookingsLoading.value = false;
  }
};

const openImageModal = (room: any) => {
  currentRoom.value = room;
  isImageModalOpen.value = true;
};

const handleImageUpload = async (event: any) => {
  const file = event.target.files[0];
  if (!file) return;

  uploadLoading.value = true;
  try {
    await roomAdminService.uploadImage(currentRoom.value.id, file);
    ui.showAlert({ title: 'สำเร็จ', message: 'อัปโหลดรูปภาพเรียบร้อยแล้ว', type: 'success' });
    await roomStore.fetchRooms();
    currentRoom.value = roomStore.rooms.find(r => r.id === currentRoom.value.id);
  } catch (err: any) {
    ui.showAlert({ title: 'ผิดพลาด', message: err.response?.data?.detail || 'อัปโหลดไม่สำเร็จ', type: 'error' });
  } finally {
    uploadLoading.value = false;
  }
};

const handleDeleteImage = async (imageId: number) => {
  try {
    await roomAdminService.deleteImage(currentRoom.value.id, imageId);
    ui.showAlert({ title: 'สำเร็จ', message: 'ลบรูปภาพเรียบร้อยแล้ว', type: 'success' });
    await roomStore.fetchRooms();
    currentRoom.value = roomStore.rooms.find(r => r.id === currentRoom.value.id);
  } catch (err: any) {
    ui.showAlert({ title: 'ผิดพลาด', message: err.response?.data?.detail || 'ลบไม่สำเร็จ', type: 'error' });
  }
};

const handleSetPrimary = async (imageId: number) => {
  try {
    await roomAdminService.setPrimaryImage(currentRoom.value.id, imageId);
    ui.showAlert({ title: 'สำเร็จ', message: 'ตั้งค่ารูปหลักเรียบร้อยแล้ว', type: 'success' });
    await roomStore.fetchRooms();
    currentRoom.value = roomStore.rooms.find(r => r.id === currentRoom.value.id);
  } catch (err: any) {
    ui.showAlert({ title: 'ผิดพลาด', message: err.response?.data?.detail || 'ตั้งค่าไม่สำเร็จ', type: 'error' });
  }
};

const handleSubmit = async () => {
  try {
    if (isEditing.value && currentRoomId.value) {
      await roomAdminService.updateRoom(currentRoomId.value, roomForm);
      ui.showAlert({ title: 'สำเร็จ', message: 'แก้ไขข้อมูลห้องเรียบร้อยแล้ว', type: 'success' });
    } else {
      await roomAdminService.createRoom(roomForm);
      ui.showAlert({ title: 'สำเร็จ', message: 'เพิ่มห้องใหม่เรียบร้อยแล้ว', type: 'success' });
    }
    isModalOpen.value = false;
    roomStore.fetchRooms();
  } catch (err: any) {
    ui.showAlert({ title: 'ผิดพลาด', message: err.response?.data?.detail || 'เกิดข้อผิดพลาด', type: 'error' });
  }
};

const handleDelete = (id: number) => {
  ui.showConfirm({
    title: 'ยืนยันการลบ',
    message: 'คุณแน่ใจหรือไม่ว่าต้องการลบห้องนี้? ข้อมูลการจองที่เกี่ยวข้องอาจได้รับผลกระทบ',
    type: 'error',
    onConfirm: async () => {
      try {
        await roomAdminService.deleteRoom(id);
        ui.showAlert({ title: 'สำเร็จ', message: 'ลบห้องเรียบร้อยแล้ว', type: 'success' });
        roomStore.fetchRooms();
      } catch (err: any) {
        ui.showAlert({ title: 'ผิดพลาด', message: err.response?.data?.detail || 'ไม่สามารถลบได้', type: 'error' });
      }
    }
  });
};
</script>

<template>
  <MainLayout>
    <div class="animate-fade-in">
      <header class="mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6">
        <div>
          <h1 class="text-3xl font-black text-base-content mb-2 tracking-tight">จัดการห้องประชุม</h1>
          <p class="text-base-content/60 font-medium">เพิ่ม แก้ไข หรือลบข้อมูลห้องประชุมในระบบ</p>
        </div>
        
        <div class="flex flex-col xl:flex-row w-full xl:w-auto gap-4">
          <!-- Status Filter -->
          <div class="flex items-center gap-3 bg-base-200/50 px-4 rounded-2xl border border-base-content/5 h-12">
            <Filter :size="14" class="opacity-40" />
            <span class="text-[10px] font-black uppercase tracking-widest opacity-40">Status</span>
            <select v-model="statusFilter" class="select select-ghost select-xs font-black focus:outline-none bg-transparent">
              <option value="all">ทุกสถานะ</option>
              <option value="active">เปิดใช้งาน (Active)</option>
              <option value="inactive">ปิดใช้งาน (Inactive)</option>
              <option value="maintenance">ปิดปรับปรุง (Maintenance)</option>
            </select>
          </div>

          <!-- Search Input -->
          <div class="relative flex-grow sm:w-80 group">
            <Search :size="18" class="absolute left-4 top-1/2 -translate-y-1/2 text-base-content/30 group-focus-within:text-primary transition-colors" />
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="ค้นหาชื่อห้องหรือสถานที่..." 
              class="input input-bordered w-full pl-12 h-12 rounded-2xl bg-base-100 border-base-content/10 focus:border-primary/30 transition-all font-medium shadow-sm"
            />
          </div>
          
          <button @click="openAddModal" class="btn btn-primary h-12 px-6 rounded-2xl gap-2 shadow-lg shadow-primary/20 font-black">
            <Plus :size="20" /> เพิ่มห้องใหม่
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
                <th class="py-5 pl-8 font-black uppercase text-[10px] tracking-widest opacity-40">ห้องประชุม</th>
                <th class="py-5 font-black uppercase text-[10px] tracking-widest opacity-40">สถานที่ / อาคาร</th>
                <th class="py-5 font-black uppercase text-[10px] tracking-widest opacity-40 text-center">ความจุ</th>
                <th class="py-5 font-black uppercase text-[10px] tracking-widest opacity-40 text-center">สถานะ</th>
                <th class="py-5 font-black uppercase text-[10px] tracking-widest opacity-40 text-right pr-8">จัดการ</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="room in paginatedRooms" :key="room.id" 
                  @click="openRoomDetail(room)"
                  class="hover:bg-primary/5 transition-all cursor-pointer group border-b border-base-content/5">
                <td class="pl-8">
                  <div class="flex items-center gap-4">
                    <div class="w-14 h-14 bg-primary/10 rounded-2xl flex items-center justify-center text-primary font-black overflow-hidden border border-base-content/5 group-hover:bg-primary group-hover:text-white transition-all shadow-sm">
                      <img v-if="room.images && room.images.find((i: any) => i.is_primary)" 
                        :src="`http://localhost:8000/${room.images.find((i: any) => i.is_primary).image_path}`" 
                        class="w-full h-full object-cover group-hover:scale-110 transition-transform" />
                      <span v-else class="text-xl">{{ room.name.charAt(0) }}</span>
                    </div>
                    <div>
                      <div class="font-black text-lg group-hover:text-primary transition-colors tracking-tight">{{ room.name }}</div>
                      <div class="text-[10px] opacity-40 font-black uppercase tracking-widest truncate max-w-xs">{{ room.description || 'ไม่มีรายละเอียด' }}</div>
                    </div>
                  </div>
                </td>
                <td>
                  <div class="flex flex-col">
                    <span class="font-bold text-sm tracking-tight">{{ room.location }}</span>
                    <span class="text-[10px] opacity-40 font-black uppercase">{{ room.building }} • {{ room.floor ? `ชั้น ${room.floor}` : 'N/A' }}</span>
                  </div>
                </td>
                <td class="text-center">
                  <div class="badge badge-neutral gap-2 font-black p-3 text-[10px]">
                    <Users :size="12" /> {{ room.capacity }}
                  </div>
                </td>
                <td class="text-center">
                  <div :class="['badge font-black p-3 uppercase tracking-widest text-[10px]', room.status === 'active' ? 'badge-success shadow-success/10' : 'badge-error shadow-error/10']">
                    {{ room.status === 'active' ? 'ใช้งานได้' : 'ปิดปรับปรุง' }}
                  </div>
                </td>
                <td class="text-right pr-8" @click.stop>
                  <div class="flex justify-end gap-1">
                    <button @click="openRoomDetail(room)" class="btn btn-ghost btn-sm btn-square text-primary tooltip" data-tip="ดูรายละเอียด / ตารางเวลา">
                      <Eye :size="20" />
                    </button>
                    <button @click="openEditModal(room)" class="btn btn-ghost btn-sm btn-square text-info tooltip" data-tip="แก้ไขข้อมูล">
                      <Edit2 :size="20" />
                    </button>
                    <button @click="openImageModal(room)" class="btn btn-ghost btn-sm btn-square text-warning tooltip" data-tip="จัดการรูปภาพ">
                      <Camera :size="20" />
                    </button>
                    <button @click="handleDelete(room.id)" class="btn btn-ghost btn-sm btn-square text-error tooltip" data-tip="ลบห้อง">
                      <Trash2 :size="20" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination Footer -->
        <!-- Pagination Footer -->
        <div v-if="totalRooms > 0" class="p-6 bg-base-200/20 border-t border-base-content/5 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div class="text-xs font-black opacity-40 uppercase tracking-widest">
            Showing {{ (currentPage - 1) * pageSize + 1 }}-{{ Math.min(currentPage * pageSize, totalRooms) }} of {{ totalRooms }} Rooms
          </div>

          <div class="join shadow-sm border border-base-content/5">
            <button 
              class="join-item btn btn-sm px-6 bg-base-100 border-0 hover:bg-primary hover:text-white" 
              :disabled="currentPage === 1"
              @click="currentPage--; fetchRooms()"
            >PREV</button>
            <button class="join-item btn btn-sm px-6 bg-base-100 border-0 font-black">PAGE {{ currentPage }}</button>
            <button 
              class="join-item btn btn-sm px-6 bg-base-100 border-0 hover:bg-primary hover:text-white" 
              :disabled="currentPage * pageSize >= totalRooms"
              @click="currentPage++; fetchRooms()"
            >NEXT</button>
          </div>
        </div>

        <div v-if="totalRooms === 0 && !roomStore.loading" class="py-32 text-center flex flex-col items-center">
          <div class="w-20 h-20 bg-base-200 rounded-full flex items-center justify-center text-base-content/20 mb-6">
            <Search :size="40" />
          </div>
          <h3 class="text-2xl font-black opacity-20 uppercase tracking-widest">ไม่พบข้อมูลห้องประชุม</h3>
          <p class="text-sm opacity-30 mt-2">ลองเปลี่ยนคำค้นหาหรือตัวกรองเพื่อหาห้องที่คุณต้องการ</p>
          <button @click="searchQuery = ''; statusFilter = 'all'" class="btn btn-ghost btn-sm mt-4 text-primary font-black uppercase tracking-widest">ล้างการค้นหา</button>
        </div>
      </div>
    </div>

    <!-- Room Detail Long Modal (World Class UX) -->
    <dialog ref="detailDialogRef" class="modal" @close="handleDetailModalClose">
      <div v-if="currentRoom" class="modal-box w-11/12 max-w-2xl p-0 bg-base-100 shadow-2xl border border-base-content/10 overflow-hidden">
        <!-- Hero Header -->
        <div class="relative h-64 overflow-hidden">
          <img v-if="currentRoom.images && currentRoom.images.find((i: any) => i.is_primary)" 
            :src="`http://localhost:8000/${currentRoom.images.find((i: any) => i.is_primary).image_path}`" 
            class="w-full h-full object-cover" />
          <div v-else class="w-full h-full bg-gradient-to-br from-primary/20 via-base-100 to-secondary/10 flex items-center justify-center text-primary text-6xl font-black">
            {{ currentRoom.name.charAt(0) }}
          </div>
          <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent flex flex-col justify-end p-10">
            <div class="badge badge-primary font-black uppercase text-[10px] tracking-widest mb-3 shadow-lg px-4 py-3">Property Insights</div>
            <h3 class="text-4xl font-black text-white leading-tight mb-2 tracking-tight">{{ currentRoom.name }}</h3>
            <div class="flex items-center gap-3 text-white/70 font-bold uppercase text-xs tracking-wide">
              <MapPin :size="14" class="text-primary" /> {{ currentRoom.location }} • {{ currentRoom.building }}
            </div>
          </div>
          <button @click="isDetailModalOpen = false" class="btn btn-sm btn-circle btn-ghost absolute right-6 top-6 bg-white/10 text-white hover:bg-white/20 backdrop-blur-md border-0">
            <X :size="20" />
          </button>
        </div>

        <div class="p-10 space-y-12 overflow-y-auto max-h-[70vh] premium-scroll">
          <!-- Room Fast Facts -->
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="bg-base-200/50 p-6 rounded-3xl border border-base-content/5 text-center">
              <div class="text-[10px] opacity-40 uppercase font-black tracking-widest mb-2">Capacity</div>
              <div class="text-2xl font-black text-primary">{{ currentRoom.capacity }}</div>
            </div>
            <div class="bg-base-200/50 p-6 rounded-3xl border border-base-content/5 text-center">
              <div class="text-[10px] opacity-40 uppercase font-black tracking-widest mb-2">Floor</div>
              <div class="text-2xl font-black text-base-content">{{ currentRoom.floor || 'N/A' }}</div>
            </div>
            <div class="bg-base-200/50 p-6 rounded-3xl border border-base-content/5 text-center">
              <div class="text-[10px] opacity-40 uppercase font-black tracking-widest mb-2">Status</div>
              <div :class="['text-[10px] font-black uppercase px-3 py-1 rounded-full mx-auto w-fit', currentRoom.status === 'active' ? 'bg-success/10 text-success' : 'bg-error/10 text-error']">{{ currentRoom.status }}</div>
            </div>
            <div class="bg-base-200/50 p-6 rounded-3xl border border-base-content/5 text-center">
              <div class="text-[10px] opacity-40 uppercase font-black tracking-widest mb-2">Building</div>
              <div class="text-sm font-black truncate">{{ currentRoom.building || 'N/A' }}</div>
            </div>
          </div>

          <!-- Description -->
          <div class="space-y-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-2xl bg-primary/10 flex items-center justify-center text-primary"><Info :size="20" /></div>
              <h4 class="text-xl font-black uppercase tracking-tight">เกี่ยวกับห้องประชุม</h4>
            </div>
            <p class="text-base font-medium leading-relaxed opacity-60 bg-base-200/30 p-6 rounded-[2rem] border border-base-content/5 italic">
              {{ currentRoom.description || 'ไม่มีข้อมูลรายละเอียดห้องพักเพิ่มเติมในระบบ' }}
            </p>
          </div>

          <!-- Upcoming Bookings (Today & Future - Top 10) -->
          <div class="space-y-6">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center text-success"><Calendar :size="20" /></div>
                <h4 class="text-xl font-black uppercase tracking-tight">ตารางการจองถัดไป (Top 10)</h4>
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
                  <h5 class="font-black text-lg group-hover:text-success transition-colors leading-tight">{{ booking.title }}</h5>
                  <div class="flex items-center gap-4 mt-2">
                    <div class="flex items-center gap-1.5 text-xs font-bold opacity-50"><Clock :size="12" /> {{ formatTime(booking.start_time) }} - {{ formatTime(booking.end_time) }}</div>
                    <div class="flex items-center gap-1.5 text-xs font-bold opacity-50"><Users :size="12" /> {{ booking.snap_user_name }}</div>
                  </div>
                </div>
                <div class="flex flex-col items-end justify-center">
                   <div class="badge badge-success badge-sm font-black text-[10px] tracking-widest px-3">CONFIRMED</div>
                </div>
              </div>
            </div>
            <div v-else-if="!bookingsLoading" class="p-12 text-center bg-base-200/20 border border-dashed border-base-content/10">
              <div class="opacity-20 font-bold">ไม่มีรายการจองในอนาคต</div>
            </div>
          </div>

          <!-- Past History (Top 10) -->
          <div class="space-y-6">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-neutral/10 flex items-center justify-center text-neutral"><History :size="20" /></div>
              <h4 class="text-xl font-black uppercase tracking-tight">ประวัติการใช้งานล่าสุด (Top 10)</h4>
            </div>

            <div v-if="pastBookings.length > 0" class="space-y-3">
              <div v-for="booking in pastBookings" :key="booking.id" class="flex gap-6 p-6 bg-base-200/20 border border-base-content/5 hover:border-neutral/20 transition-all group grayscale hover:grayscale-0 opacity-60 hover:opacity-100">
                <div class="flex flex-col items-center justify-center min-w-[70px] border-r border-base-content/5 pr-6">
                  <div class="text-xl font-black opacity-50">{{ new Date(booking.start_time).getDate() }}</div>
                  <div class="text-[10px] font-black uppercase opacity-30">{{ new Date(booking.start_time).toLocaleString('en-US', { month: 'short' }) }}</div>
                </div>
                <div class="flex-grow">
                  <h5 class="font-bold text-base leading-tight opacity-70 group-hover:opacity-100">{{ booking.title }}</h5>
                  <div class="flex items-center gap-4 mt-1">
                    <div class="text-[10px] font-bold opacity-40">{{ formatTime(booking.start_time) }} - {{ formatTime(booking.end_time) }}</div>
                    <div class="text-[10px] font-bold opacity-40">{{ booking.snap_user_name }}</div>
                  </div>
                </div>
                <div class="flex flex-col items-end justify-center">
                   <div class="badge badge-ghost badge-sm font-black text-[10px] tracking-widest px-3 opacity-30">ARCHIVED</div>
                </div>
              </div>
            </div>
            <div v-else-if="!bookingsLoading" class="p-12 text-center bg-base-200/10 border border-dashed border-base-content/5">
              <div class="opacity-10 font-bold">ไม่มีประวัติการใช้งานย้อนหลัง</div>
            </div>
          </div>
        </div>

        <div class="p-8 bg-base-200/50 border-t border-base-content/5 flex gap-4">
           <button @click="isDetailModalOpen = false; openEditModal(currentRoom)" class="btn btn-primary flex-grow font-black gap-2 shadow-lg shadow-primary/20">
             <Edit2 :size="18" /> แก้ไขการตั้งค่าห้อง
           </button>
           <button @click="isDetailModalOpen = false" class="btn btn-ghost px-10">ปิด</button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="isDetailModalOpen = false">
        <button>close</button>
      </form>
    </dialog>

    <!-- Add/Edit Modal -->
    <dialog ref="modalDialogRef" class="modal" @close="handleModalClose">
      <div class="modal-box max-w-2xl bg-base-100 border border-base-content/10 shadow-2xl p-8">
        <h3 class="font-black text-3xl mb-8 flex items-center gap-3">
          <Edit2 v-if="isEditing" class="text-primary" />
          <Plus v-else class="text-primary" />
          {{ isEditing ? 'แก้ไขข้อมูลห้อง' : 'เพิ่มห้องประชุมใหม่' }}
        </h3>
        
        <form @submit.prevent="handleSubmit" class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="form-control col-span-2">
            <label class="label"><span class="label-text font-black uppercase text-[10px] tracking-widest opacity-50">ชื่อห้องประชุม</span></label>
            <input v-model="roomForm.name" type="text" class="input input-bordered focus:input-primary font-bold" placeholder="เช่น Room 101" required />
          </div>

          <div class="form-control">
            <label class="label"><span class="label-text font-black uppercase text-[10px] tracking-widest opacity-50">ความจุ (คน)</span></label>
            <input v-model="roomForm.capacity" type="number" class="input input-bordered focus:input-primary font-bold" required />
          </div>

          <div class="form-control">
            <label class="label"><span class="label-text font-black uppercase text-[10px] tracking-widest opacity-50">สถานะ</span></label>
            <select v-model="roomForm.status" class="select select-bordered focus:select-primary font-bold">
              <option value="active">ใช้งานได้ (Active)</option>
              <option value="maintenance">ปิดปรับปรุง (Maintenance)</option>
              <option value="inactive">ยกเลิกใช้งาน (Inactive)</option>
            </select>
          </div>

          <div class="form-control">
            <label class="label"><span class="label-text font-black uppercase text-[10px] tracking-widest opacity-50">อาคาร</span></label>
            <input v-model="roomForm.building" type="text" class="input input-bordered focus:input-primary font-bold" />
          </div>

          <div class="form-control">
            <label class="label"><span class="label-text font-black uppercase text-[10px] tracking-widest opacity-50">ชั้น</span></label>
            <input v-model="roomForm.floor" type="text" class="input input-bordered focus:input-primary font-bold" />
          </div>

          <div class="form-control col-span-2">
            <label class="label"><span class="label-text font-black uppercase text-[10px] tracking-widest opacity-50">สถานที่ระบุชัดเจน</span></label>
            <input v-model="roomForm.location" type="text" class="input input-bordered focus:input-primary font-bold" placeholder="เช่น ชั้น 3 ฝั่งตะวันออก ติดลิฟต์" />
          </div>

          <div class="form-control col-span-2">
            <label class="label"><span class="label-text font-black uppercase text-[10px] tracking-widest opacity-50">รายละเอียดเพิ่มเติม</span></label>
            <textarea v-model="roomForm.description" class="textarea textarea-bordered h-24 focus:textarea-primary font-medium" placeholder="ระบุสิ่งอำนวยความสะดวก..."></textarea>
          </div>

          <div class="modal-action col-span-2 gap-2 mt-4">
            <button type="button" class="btn btn-ghost font-bold" @click="isModalOpen = false">ยกเลิก</button>
            <button type="submit" class="btn btn-primary px-10 font-black shadow-lg shadow-primary/20">
              <Check :size="20" /> บันทึกข้อมูล
            </button>
          </div>
        </form>
      </div>
      <form method="dialog" class="modal-backdrop" @click="isModalOpen = false">
        <button>close</button>
      </form>
    </dialog>

    <!-- Image Management Modal -->
    <dialog ref="imageDialogRef" class="modal" @close="handleImageModalClose">
      <div class="modal-box max-w-4xl bg-base-100 border border-base-content/10 shadow-2xl p-8">
        <div class="flex justify-between items-center mb-8">
          <h3 class="font-black text-3xl flex items-center gap-3">
            <Camera class="text-primary" />
            จัดการรูปภาพ: {{ currentRoom?.name }}
          </h3>
          <button @click="isImageModalOpen = false" class="btn btn-sm btn-circle btn-ghost"><X :size="20" /></button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <!-- Upload Placeholder -->
          <div class="aspect-video rounded-3xl border-2 border-dashed border-base-content/10 flex flex-col items-center justify-center gap-4 bg-base-200/30 hover:bg-base-200/50 transition-all cursor-pointer relative group">
            <input type="file" @change="handleImageUpload" class="absolute inset-0 opacity-0 cursor-pointer" accept="image/*" :disabled="uploadLoading" />
            <div v-if="uploadLoading" class="loading loading-spinner loading-lg text-primary"></div>
            <template v-else>
              <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
                <Plus :size="24" />
              </div>
              <span class="text-[10px] font-black opacity-40 uppercase tracking-[0.2em]">อัปโหลดรูปภาพ</span>
            </template>
          </div>

          <!-- Existing Images -->
          <div v-for="img in currentRoom?.images" :key="img.id" 
            class="aspect-video rounded-3xl overflow-hidden relative border border-base-content/5 group shadow-lg">
            <img :src="`http://localhost:8000/${img.image_path}`" class="w-full h-full object-cover" />
            
            <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
              <button @click="handleSetPrimary(img.id)" 
                class="btn btn-sm btn-circle shadow-lg" :class="img.is_primary ? 'btn-success' : 'btn-ghost bg-white/20'"
                :title="img.is_primary ? 'รูปหลัก' : 'ตั้งเป็นรูปหลัก'">
                <Check :size="16" />
              </button>
              <button @click="handleDeleteImage(img.id)" class="btn btn-sm btn-circle btn-error shadow-lg" title="ลบรูปภาพ">
                <Trash2 :size="16" />
              </button>
            </div>

            <div v-if="img.is_primary" class="absolute top-3 left-3">
              <div class="badge badge-success badge-sm font-black text-[10px] tracking-widest shadow-lg">PRIMARY</div>
            </div>
          </div>
        </div>

        <div class="modal-action">
          <button class="btn btn-primary px-10 font-black shadow-lg shadow-primary/20" @click="isImageModalOpen = false">เสร็จสิ้น</button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="isImageModalOpen = false">
        <button>close</button>
      </form>
    </dialog>
  </MainLayout>
</template>
