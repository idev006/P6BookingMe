<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { 
  X, 
  MapPin, 
  User, 
  Calendar, 
  Clock, 
  Users, 
  FileText, 
  CheckCircle2, 
  AlertCircle,
  Building2,
  Mail,
  Briefcase,
  Layout,
  ShieldCheck,
  Pencil,
  Copy,
  XCircle
} from 'lucide-vue-next';
import { formatDate, formatTime } from '../../utils/format';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';
import { useApprovalStore } from '../../stores/approval';
import { useUIStore } from '../../stores/ui';

const props = defineProps<{
  isOpen: boolean;
  booking: any | null;
}>();

const emit = defineEmits(['close', 'refresh']);
const dialogRef = ref<HTMLDialogElement | null>(null);
const router = useRouter();
const auth = useAuthStore();
const approvalStore = useApprovalStore();
const ui = useUIStore();

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    dialogRef.value?.showModal();
  } else {
    dialogRef.value?.close();
  }
});

const handleClose = () => {
  emit('close');
};

const handleEdit = () => {
  if (!props.booking) return;
  emit('close');
  router.push({
    name: 'Booking',
    params: { id: props.booking.room_id },
    query: { edit: props.booking.id }
  });
};

const handleDuplicate = () => {
  if (!props.booking) return;
  emit('close');
  router.push({
    name: 'Booking',
    params: { id: props.booking.room_id },
    query: { duplicate: props.booking.id }
  });
};

const handleApprove = async () => {
  if (!props.booking) return;
  ui.showConfirm({
    title: 'ยืนยันการอนุมัติ',
    message: `คุณต้องการอนุมัติการจอง "${props.booking.title}" ใช่หรือไม่?`,
    onConfirm: async () => {
      try {
        await approvalStore.approve(props.booking.id);
        ui.showAlert({ title: 'สำเร็จ', message: 'อนุมัติการจองเรียบร้อยแล้ว', type: 'success' });
        emit('refresh');
        emit('close');
      } catch (err) {
        ui.showAlert({ title: 'เกิดข้อผิดพลาด', message: 'ไม่สามารถอนุมัติได้', type: 'error' });
      }
    }
  });
};

const handleReject = async () => {
  if (!props.booking) return;
  
  // Quick reason prompt using browser prompt for now, or we could add a ref for it
  const reason = window.prompt('กรุณาระบุเหตุผลในการปฏิเสธ:');
  if (reason === null) return;
  if (!reason.trim()) {
    ui.showAlert({ title: 'คำเตือน', message: 'กรุณาระบุเหตุผล', type: 'warning' });
    return;
  }

  try {
    await approvalStore.reject(props.booking.id, reason);
    ui.showAlert({ title: 'สำเร็จ', message: 'ปฏิเสธการจองเรียบร้อยแล้ว', type: 'success' });
    emit('refresh');
    emit('close');
  } catch (err) {
    ui.showAlert({ title: 'เกิดข้อผิดพลาด', message: 'ไม่สามารถปฏิเสธได้', type: 'error' });
  }
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case 'confirmed': return 'badge-success';
    case 'pending': return 'badge-warning';
    case 'rejected': return 'badge-error';
    case 'cancelled': return 'badge-neutral';
    default: return 'badge-ghost';
  }
};

const isOwner = computed(() => props.booking?.user_id === auth.user?.id || auth.isAdmin);
const canEdit = computed(() => props.booking?.status === 'pending' || props.booking?.status === 'confirmed');
const isPending = computed(() => props.booking?.status === 'pending');
</script>

<template>
  <dialog ref="dialogRef" class="modal" @close="handleClose">
    <div v-if="booking" class="modal-box w-11/12 max-w-2xl p-0 bg-base-100 shadow-2xl border border-base-content/10 overflow-hidden">
      <!-- Header Section (Fixed Gradient) -->
      <div class="relative bg-gradient-to-br from-primary/10 via-base-100 to-secondary/5 p-10 border-b border-base-content/5">
        <button @click="emit('close')" class="btn btn-sm btn-circle btn-ghost absolute right-6 top-6 z-10">
          <X :size="20" />
        </button>
        
        <div class="space-y-4">
          <div class="flex items-center gap-2">
            <span class="text-[10px] font-black opacity-30 tracking-[0.2em] uppercase">Booking ID #{{ booking.id }}</span>
            <div :class="['badge badge-sm font-black uppercase py-3 px-4 shadow-sm', getStatusBadge(booking.status)]">
              {{ booking.status }}
            </div>
          </div>
          <h2 class="text-3xl font-black text-base-content tracking-tight leading-tight">{{ booking.title }}</h2>
        </div>
      </div>

      <!-- Long Modal Content (Scrollable) -->
      <div class="p-10 max-h-[70vh] overflow-y-auto premium-scroll space-y-12">
        
        <!-- Section: Time & Date -->
        <section class="space-y-6">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded bg-primary/10 flex items-center justify-center text-primary"><Calendar :size="20" /></div>
            <h4 class="text-xl font-black uppercase tracking-tight">วันและเวลา</h4>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="flex items-center gap-4 p-4 bg-base-200/30 border border-base-content/5">
              <div class="w-10 h-10 rounded bg-primary/10 flex items-center justify-center text-primary"><Calendar :size="20" /></div>
              <div>
                <div class="text-[10px] opacity-40 uppercase font-black">วันที่จอง</div>
                <div class="font-bold">{{ formatDate(booking.start_time) }}</div>
              </div>
            </div>
            <div class="flex items-center gap-4 p-4 bg-base-200/30 border border-base-content/5">
              <div class="w-10 h-10 rounded bg-secondary/10 flex items-center justify-center text-secondary"><Clock :size="20" /></div>
              <div>
                <div class="text-[10px] opacity-40 uppercase font-black">เวลา</div>
                <div class="font-bold">{{ formatTime(booking.start_time) }} - {{ formatTime(booking.end_time) }}</div>
              </div>
            </div>
          </div>
        </section>

        <!-- Section: Agenda -->
        <section class="space-y-4">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded bg-neutral/10 flex items-center justify-center text-neutral"><FileText :size="20" /></div>
            <h4 class="text-xl font-black uppercase tracking-tight">วาระการประชุม</h4>
          </div>
          <div class="p-8 bg-base-200/50 border border-base-content/5 relative overflow-hidden group min-h-[120px]">
            <div class="absolute top-0 left-0 w-1.5 h-full bg-primary opacity-20 group-hover:opacity-100 transition-opacity"></div>
            <p class="text-lg leading-relaxed font-medium text-base-content/80 whitespace-pre-wrap">
              {{ booking.description || 'ไม่มีรายละเอียดวาระการประชุมเพิ่มเติม' }}
            </p>
          </div>
        </section>

        <!-- Section: Venue Information -->
        <section class="space-y-6">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded bg-primary/10 flex items-center justify-center text-primary"><MapPin :size="20" /></div>
            <h4 class="text-xl font-black uppercase tracking-tight">ข้อมูลสถานที่</h4>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="p-6 bg-base-200/50 border border-base-content/5 flex items-center gap-4">
              <div class="w-12 h-12 bg-base-100 flex items-center justify-center shadow-sm">
                <Building2 :size="24" class="opacity-40" />
              </div>
              <div>
                <div class="text-[10px] opacity-40 uppercase font-black tracking-widest">ชื่อห้องประชุม</div>
                <div class="font-bold text-lg leading-tight">{{ booking.snap_room_name }}</div>
                <div class="text-[10px] opacity-50 mt-1 uppercase">{{ booking.snap_room_location }}</div>
              </div>
            </div>
            <div class="p-6 bg-base-200/50 border border-base-content/5 flex items-center gap-4">
              <div class="w-12 h-12 bg-base-100 flex items-center justify-center shadow-sm">
                <Users :size="24" class="text-secondary" />
              </div>
              <div>
                <div class="text-[10px] opacity-40 uppercase font-black tracking-widest">จำนวนผู้เข้าร่วม</div>
                <div class="text-xl font-black">{{ booking.attendee_count }} <small class="text-xs opacity-40">/ {{ booking.snap_room_capacity }}</small></div>
              </div>
            </div>
          </div>
        </section>

        <!-- Section: Requester Profile -->
        <section class="space-y-6">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded bg-secondary/10 flex items-center justify-center text-secondary"><User :size="20" /></div>
            <h4 class="text-xl font-black uppercase tracking-tight">ข้อมูลผู้จอง</h4>
          </div>
          <div class="flex items-center gap-6 p-6 bg-base-200/30 border border-base-content/5">
            <div class="avatar placeholder">
              <div class="bg-primary text-primary-content w-20 h-20 flex items-center justify-center shadow-xl shadow-primary/10 ring-4 ring-white">
                <span class="text-3xl font-black">{{ booking.snap_user_name?.charAt(0) }}</span>
              </div>
            </div>
            <div class="space-y-2">
              <div class="text-2xl font-black leading-tight">{{ booking.snap_user_name }}</div>
              <div class="flex flex-wrap gap-3">
                <div class="flex items-center gap-1.5 text-xs font-bold opacity-50"><Mail :size="14" /> {{ booking.snap_user_email }}</div>
                <div class="flex items-center gap-1.5 text-xs font-bold opacity-50"><Briefcase :size="14" /> {{ booking.snap_user_department || 'N/A' }}</div>
              </div>
            </div>
          </div>
        </section>

        <!-- Section: Approval History -->
        <section class="space-y-6">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center text-success"><ShieldCheck :size="20" /></div>
            <h4 class="text-xl font-black uppercase tracking-tight">สถานะและการอนุมัติ</h4>
          </div>

          <div v-if="booking.status === 'confirmed' || booking.status === 'rejected'" class="p-8 bg-base-200/50 border border-base-content/5">
            <div class="flex items-center gap-4 mb-8">
              <div :class="['w-16 h-16 flex items-center justify-center shadow-lg', booking.status === 'confirmed' ? 'bg-success text-white' : 'bg-error text-white']">
                <CheckCircle2 v-if="booking.status === 'confirmed'" :size="32" />
                <AlertCircle v-else :size="32" />
              </div>
              <div>
                <div class="text-[10px] opacity-40 uppercase font-black tracking-widest">สถานะปัจจุบัน</div>
                <div class="text-2xl font-black">{{ booking.status === 'confirmed' ? 'อนุมัติแล้ว' : 'ปฏิเสธ' }}</div>
              </div>
            </div>
            
            <div v-if="booking.approved_by_name" class="grid grid-cols-1 md:grid-cols-2 gap-8 py-6 border-t border-base-content/10">
              <div class="space-y-1">
                <div class="text-[10px] opacity-40 uppercase font-black tracking-widest">ผู้อนุมัติ</div>
                <div class="font-bold flex items-center gap-2 text-sm">{{ booking.approved_by_name }}</div>
              </div>
              <div v-if="booking.approved_at" class="space-y-1">
                <div class="text-[10px] opacity-40 uppercase font-black tracking-widest">เวลาที่ดำเนินการ</div>
                <div class="font-bold text-sm">{{ formatDate(booking.approved_at) }} {{ formatTime(booking.approved_at) }}</div>
              </div>
            </div>

            <div v-if="booking.approval_note" class="mt-4 p-6 bg-base-100 border border-base-content/5 italic text-sm opacity-70 shadow-inner">
              "{{ booking.approval_note }}"
            </div>
          </div>

          <div v-else-if="booking.status === 'cancelled'" class="p-10 bg-neutral/5 border border-neutral/10 flex flex-col items-center text-center">
             <div class="w-16 h-16 bg-neutral/10 rounded-full flex items-center justify-center text-neutral mb-4">
               <X :size="32" />
             </div>
             <div class="text-2xl font-black text-neutral">รายการถูกยกเลิกแล้ว</div>
             <p v-if="booking.cancel_reason" class="mt-4 text-sm opacity-60 max-w-xs">{{ booking.cancel_reason }}</p>
          </div>

          <div v-else class="py-20 text-center bg-warning/5 border border-dashed border-warning/20 flex flex-col items-center">
            <div class="w-20 h-20 bg-warning/10 rounded-full flex items-center justify-center text-warning mb-6 animate-pulse">
              <Clock :size="40" />
            </div>
            <h5 class="text-xl font-black text-warning uppercase">อยู่ระหว่างการพิจารณา</h5>
            <p class="text-sm opacity-40 mt-2">โปรดรอการตรวจสอบจากผู้ดูแลระบบ</p>
          </div>
        </section>
      </div>

      <!-- Footer Action -->
      <div class="p-8 bg-base-200/50 border-t border-base-content/5 flex flex-wrap justify-end gap-3">
        <!-- Approver Actions -->
        <template v-if="(auth.isApprover || auth.isAdmin) && isPending">
          <button @click="handleReject" class="btn btn-error btn-outline gap-2 rounded-xl px-6">
            <XCircle :size="18" /> ปฏิเสธ (Reject)
          </button>
          <button @click="handleApprove" class="btn btn-success gap-2 rounded-xl px-6 shadow-lg shadow-success/20">
            <CheckCircle2 :size="18" /> อนุมัติ (Approve)
          </button>
          <div class="divider divider-horizontal mx-2 opacity-10"></div>
        </template>

        <button v-if="isOwner && canEdit" @click="handleEdit" class="btn btn-outline btn-info gap-2 rounded-xl px-6">
          <Pencil :size="16" /> แก้ไขการจอง
        </button>
        <button @click="handleDuplicate" class="btn btn-outline btn-success gap-2 rounded-xl px-6">
          <Copy :size="16" /> จองอีกครั้ง (Duplicate)
        </button>
        <button @click="emit('close')" class="btn btn-ghost px-12 font-black uppercase tracking-widest text-xs">ปิดหน้าต่าง</button>
      </div>
    </div>
  </dialog>
</template>

<style scoped>
.premium-scroll::-webkit-scrollbar {
  width: 5px;
}
.premium-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.premium-scroll::-webkit-scrollbar-thumb {
  background: oklch(var(--bc) / 0.1);
  border-radius: 10px;
}
.premium-scroll::-webkit-scrollbar-thumb:hover {
  background: oklch(var(--p) / 0.3);
}
</style>
