<script setup lang="ts">
import { reactive, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import MainLayout from '../components/layout/MainLayout.vue';
import { useRoomStore } from '../stores/room';
import { useBookingStore } from '../stores/booking';
import { useUIStore } from '../stores/ui';
import { Clock, Users, ChevronLeft, Info, Calendar as CalendarIcon } from 'lucide-vue-next';
import DatePicker from 'primevue/datepicker';
import { 
  getLocalTimeZone, 
  today
} from '@internationalized/date';
import { getImageUrl } from '../utils/format';

const route = useRoute();
const router = useRouter();
const roomStore = useRoomStore();
const bookingStore = useBookingStore();
const ui = useUIStore();

const roomId = parseInt(route.params.id as string);
const editId = route.query.edit ? parseInt(route.query.edit as string) : null;
const duplicateId = route.query.duplicate ? parseInt(route.query.duplicate as string) : null;
const isEdit = !!editId;
const isDuplicate = !!duplicateId;

// Standardize date to YYYY-MM-DD string for native input
const form = reactive({
  title: '',
  description: '',
  attendee_count: 2,
  date: today(getLocalTimeZone()).toString(), // "2026-05-09"
  start_time: '09:00',
  end_time: '10:00',
});

onMounted(async () => {
  roomStore.fetchRoomDetail(roomId);
  
  if (isEdit || isDuplicate) {
    const id = editId || duplicateId;
    if (id) {
      try {
        const booking = await bookingStore.getBookingDetail(id);
        form.title = booking.title;
        form.description = booking.description;
        form.attendee_count = booking.attendee_count;
        
        const start = new Date(booking.start_time);
        const end = new Date(booking.end_time);
        
        form.date = `${start.getFullYear()}-${String(start.getMonth() + 1).padStart(2, '0')}-${String(start.getDate()).padStart(2, '0')}`;
        form.start_time = `${String(start.getHours()).padStart(2, '0')}:${String(start.getMinutes()).padStart(2, '0')}`;
        form.end_time = `${String(end.getHours()).padStart(2, '0')}:${String(end.getMinutes()).padStart(2, '0')}`;
      } catch (err) {
        ui.showAlert({ title: 'ข้อผิดพลาด', message: 'ไม่สามารถดึงข้อมูลการจองเดิมได้', type: 'error' });
      }
    }
  }
});

const handleSubmit = async () => {
  // Ensure date is formatted as YYYY-MM-DD
  let dateStr = form.date;
  if (form.date instanceof Date) {
    const year = form.date.getFullYear();
    const month = String(form.date.getMonth() + 1).padStart(2, '0');
    const day = String(form.date.getDate()).padStart(2, '0');
    dateStr = `${year}-${month}-${day}`;
  }

  const startStr = `${dateStr}T${form.start_time}:00`;
  const endStr = `${dateStr}T${form.end_time}:00`;

  try {
    const payload = {
      room_id: roomId,
      title: form.title,
      description: form.description,
      attendee_count: form.attendee_count,
      start_time: startStr,
      end_time: endStr,
    };

    if (isEdit) {
      await bookingStore.updateBooking(editId!, payload);
      ui.showAlert({
        title: 'แก้ไขสำเร็จ!',
        message: 'ข้อมูลการจองของคุณได้รับการอัปเดตแล้ว',
        type: 'success',
        onConfirm: () => router.push('/dashboard')
      });
    } else {
      await bookingStore.createBooking(payload);
      ui.showAlert({
        title: 'จองห้องสำเร็จ!',
        message: isDuplicate ? 'จองห้องซ้ำเรียบร้อยแล้ว' : 'คำขอจองของคุณถูกส่งไปยังผู้อนุมัติแล้ว สามารถตรวจสอบสถานะได้ที่หน้า Dashboard',
        type: 'success',
        onConfirm: () => router.push('/dashboard')
      });
    }
  } catch (err: any) {
    ui.showAlert({
      title: 'ไม่สามารถดำเนินการได้',
      message: err.response?.data?.detail || 'เกิดข้อผิดพลาดในการดำเนินการ',
      type: 'error'
    });
  }
};

const roomImage = (room: any) => {
  if (!room || !room.images || room.images.length === 0) return '';
  const primary = room.images.find((img: any) => img.is_primary);
  return getImageUrl(primary ? primary.image_path : room.images[0].image_path);
};
</script>

<template>
  <MainLayout>
    <div class="max-w-4xl mx-auto animate-fade-in px-4 pb-12">
      <button @click="router.back()" class="btn btn-ghost gap-2 mb-8 rounded-2xl hover:bg-base-200">
        <ChevronLeft :size="20" /> ย้อนกลับ
      </button>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        <!-- Form Section -->
        <div class="lg:col-span-2 order-2 lg:order-1">
          <div class="card bg-base-100 shadow-2xl border border-base-content/5 rounded-[2.5rem] overflow-hidden">
            <div class="card-body p-8 lg:p-10">
              <div class="flex items-center gap-4 mb-8">
                <div class="p-3 bg-primary/10 text-primary rounded-2xl">
                  <CalendarIcon :size="24" />
                </div>
                <h2 class="text-3xl font-black text-base-content tracking-tight">{{ isEdit ? 'แก้ไขการจอง' : 'จองห้องประชุม' }}</h2>
              </div>
              
              <form @submit.prevent="handleSubmit" class="flex flex-col gap-6">
                <div class="form-control w-full">
                  <label class="label"><span class="label-text font-black uppercase text-[10px] tracking-widest opacity-50">Meeting Title</span></label>
                  <input v-model="form.title" type="text" placeholder="ระบุหัวข้อประชุมที่ชัดเจน" class="input input-bordered w-full rounded-2xl h-14 font-bold focus:ring-2 focus:ring-primary/20" required />
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="form-control w-full">
                    <label class="label"><span class="label-text font-black uppercase text-[10px] tracking-widest opacity-50">Select Date</span></label>
                    <DatePicker 
                      v-model="form.date" 
                      dateFormat="yy-mm-dd" 
                      showIcon 
                      fluid
                      iconDisplay="input" 
                      class="prime-datepicker-custom"
                      placeholder="เลือกวันที่ประชุม"
                    />
                  </div>
                  <div class="form-control w-full">
                    <label class="label"><span class="label-text font-black uppercase text-[10px] tracking-widest opacity-50">Participants</span></label>
                    <div class="join w-full shadow-sm rounded-2xl border border-base-content/10 overflow-hidden">
                      <button type="button" @click="form.attendee_count = Math.max(1, form.attendee_count - 1)" class="btn btn-ghost join-item w-1/4 h-14">-</button>
                      <input v-model="form.attendee_count" type="number" class="input bg-base-200/30 join-item w-2/4 h-14 text-center font-bold border-0 focus:outline-none" />
                      <button type="button" @click="form.attendee_count++" class="btn btn-ghost join-item w-1/4 h-14">+</button>
                    </div>
                  </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="form-control w-full">
                    <label class="label"><span class="label-text font-black uppercase text-[10px] tracking-widest opacity-50">Start Time</span></label>
                    <input v-model="form.start_time" type="time" class="input input-bordered w-full h-14 rounded-2xl font-bold" required />
                  </div>
                  <div class="form-control w-full">
                    <label class="label"><span class="label-text font-black uppercase text-[10px] tracking-widest opacity-50">End Time</span></label>
                    <input v-model="form.end_time" type="time" class="input input-bordered w-full h-14 rounded-2xl font-bold" required />
                  </div>
                </div>

                <div class="form-control w-full">
                  <label class="label"><span class="label-text font-black uppercase text-[10px] tracking-widest opacity-50">Notes & Description</span></label>
                  <textarea v-model="form.description" class="textarea textarea-bordered h-32 rounded-2xl p-4 font-medium" placeholder="รายละเอียดเพิ่มเติม หรือสิ่งที่ต้องการเตรียมตัวสำหรับการประชุมครั้งนี้..."></textarea>
                </div>

                <div class="mt-4">
                  <button type="submit" class="btn btn-primary w-full h-16 rounded-2xl shadow-xl shadow-primary/20 text-lg font-black gap-3" :disabled="bookingStore.loading">
                    <span v-if="bookingStore.loading" class="loading loading-spinner"></span>
                    {{ isEdit ? 'บันทึกการแก้ไข' : (isDuplicate ? 'จองห้องนี้อีกครั้ง' : 'ยืนยันการจองห้อง') }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <!-- Info Sidebar -->
        <div class="lg:col-span-1 order-1 lg:order-2 sticky top-24">
          <div class="card bg-base-200 border border-base-content/5 rounded-[2.5rem] overflow-hidden shadow-xl">
            <figure v-if="roomStore.selectedRoom" class="h-56 relative">
              <img v-if="roomImage(roomStore.selectedRoom)" :src="roomImage(roomStore.selectedRoom)" alt="Room" class="w-full h-full object-cover" />
              <div v-else class="w-full h-full flex items-center justify-center bg-base-300 text-base-content/20">
                 <Info :size="60" />
              </div>
              <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end p-6">
                <span class="badge badge-primary font-bold shadow-lg shadow-primary/20 uppercase text-[10px]">Room Profile</span>
              </div>
            </figure>
            
            <div class="card-body p-8">
              <div v-if="roomStore.selectedRoom" class="space-y-6">
                <div>
                  <h3 class="text-2xl font-black leading-tight text-base-content">{{ roomStore.selectedRoom.name }}</h3>
                  <div class="flex items-center gap-2 mt-1 text-sm font-bold opacity-50 uppercase tracking-tighter">
                    <Clock :size="14" /> {{ roomStore.selectedRoom.location }}
                  </div>
                </div>
                
                <div class="divider my-0 opacity-10"></div>
                
                <div class="flex items-center justify-between">
                  <span class="flex items-center gap-2 text-xs font-black uppercase opacity-40 tracking-widest"><Users :size="14" /> Capacity</span>
                  <span class="text-xl font-black text-primary">{{ roomStore.selectedRoom.capacity }} <small class="text-[10px] font-bold opacity-60">คน</small></span>
                </div>

                <div class="space-y-3">
                  <span class="text-[10px] font-black opacity-30 uppercase tracking-[0.2em]">Equipment</span>
                  <div class="flex flex-wrap gap-2">
                    <div v-for="eq in roomStore.selectedRoom.equipment" :key="eq.id" class="px-3 py-1 bg-base-100 rounded-full text-[10px] font-black border border-base-content/5 shadow-sm">
                      {{ eq.name }}
                    </div>
                  </div>
                </div>

                <div class="bg-primary/5 p-4 rounded-2xl border border-primary/10 mt-6">
                  <p class="text-[10px] font-black text-primary leading-relaxed opacity-80 uppercase tracking-wide">
                    ⚠️ ตรวจสอบวันและเวลาให้ถูกต้องก่อนยืนยัน เพื่อป้องกันการจองซ้ำซ้อน
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>
