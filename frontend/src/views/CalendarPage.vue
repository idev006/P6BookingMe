<script setup lang="ts">
import 'temporal-polyfill/global'
import { ref, onMounted, shallowRef, watch } from 'vue';
import MainLayout from '../components/layout/MainLayout.vue';
import api from '../services/api';
import { useRoomStore } from '../stores/room';
import { useAuthStore } from '../stores/auth';
import { useUIStore } from '../stores/ui';
import BookingDetailModal from '../components/booking/BookingDetailModal.vue';
import { Calendar as CalendarIcon, RefreshCcw, MapPin } from 'lucide-vue-next';

// Schedule-X Imports
import { ScheduleXCalendar } from '@schedule-x/vue'
import { 
  createCalendar, 
  createViewDay, 
  createViewWeek, 
  createViewMonthGrid,
  createViewMonthAgenda
} from '@schedule-x/calendar'
import { createDragAndDropPlugin } from '@schedule-x/drag-and-drop'
import '@schedule-x/theme-default/dist/index.css'

const roomStore = useRoomStore();
const authStore = useAuthStore();
const ui = useUIStore();

const loading = ref(false);
const calendarApp = shallowRef<any>(null);

// Modal State
const isModalOpen = ref(false);
const selectedEvent = ref<any>(null);
const dialogRef = ref<HTMLDialogElement | null>(null);

watch(isModalOpen, (newVal) => {
  if (newVal) {
    dialogRef.value?.showModal();
  } else {
    dialogRef.value?.close();
  }
});

// Filters
const selectedRoomId = ref<number | ''>('');
const isPendingOnly = ref<boolean>(false);

// --- Temporal ZonedDateTime Mapper ---
const mapBookingToEvent = (b: any) => {
  try {
    if (!b.start_time || !b.end_time) return null;
    const tzSuffix = '+07:00[Asia/Bangkok]';
    const startIso = b.start_time.replace(' ', 'T').split('.')[0] + tzSuffix;
    const endIso = b.end_time.replace(' ', 'T').split('.')[0] + tzSuffix;

    return {
      id: String(b.id),
      title: b.title || 'ไม่มีชื่อการจอง',
      start: (window as any).Temporal.ZonedDateTime.from(startIso),
      end: (window as any).Temporal.ZonedDateTime.from(endIso),
      description: `${b.snap_room_name || ''} - ผู้จอง: ${b.snap_user_name || ''}`,
      status: b.status || 'pending',
      calendarId: b.status || 'pending',
      // Flatten snapshot fields for easier access in Schedule-X modals
      snap_room_name: b.snap_room_name,
      snap_room_location: b.snap_room_location,
      snap_user_name: b.snap_user_name,
      snap_user_email: b.snap_user_email,
      snap_user_department: b.snap_user_department,
      attendee_count: b.attendee_count,
      snap_room_capacity: b.snap_room_capacity,
      description_text: b.description || 'ไม่มีรายละเอียดเพิ่มเติม',
      created_at: b.created_at,
      // Approval metadata
      approved_by_name: b.approved_by_name || 'N/A', 
      approval_note: b.approval_note,
      approved_at: b.approved_at,
      _booking: b
    };
  } catch (e) {
    return null;
  }
};

const fetchBookings = async () => {
  loading.value = true;
  try {
    const now = new Date();
    const startRange = new Date(now.getFullYear(), now.getMonth() - 2, 1);
    const endRange = new Date(now.getFullYear(), now.getMonth() + 3, 0);

    let url = `/calendar?start_date=${startRange.toISOString()}&end_date=${endRange.toISOString()}`;
    if (selectedRoomId.value) url += `&room_id=${selectedRoomId.value}`;
    if (isPendingOnly.value) url += `&status=pending`;

    const response = await api.get(url);
    const events = (response.data.data || [])
      .map(mapBookingToEvent)
      .filter((e: any) => e !== null);

    if (calendarApp.value) {
      calendarApp.value.events.set(events);
    } else {
      initCalendar(events);
    }
  } catch (err) {
    console.error('Fetch error:', err);
  } finally {
    loading.value = false;
  }
};

const initCalendar = (initialEvents: any[] = []) => {
  try {
    const plugins = [];
    if (authStore.isAdmin) {
      plugins.push(createDragAndDropPlugin());
    }

    calendarApp.value = createCalendar({
      views: [createViewMonthGrid(), createViewMonthAgenda(), createViewWeek(), createViewDay()],
      defaultView: 'month-grid',
      events: initialEvents,
      plugins,
      timezone: 'Asia/Bangkok',
      calendars: {
        confirmed: {
          colorName: 'confirmed',
          lightColors: { main: '#22c55e', container: '#dcfce7', onContainer: '#166534' },
          darkColors: { main: '#22c55e', container: '#166534', onContainer: '#dcfce7' },
        },
        pending: {
          colorName: 'pending',
          lightColors: { main: '#f59e0b', container: '#fef3c7', onContainer: '#92400e' },
          darkColors: { main: '#f59e0b', container: '#92400e', onContainer: '#fef3c7' },
        },
        rejected: {
          colorName: 'rejected',
          lightColors: { main: '#ef4444', container: '#fee2e2', onContainer: '#991b1b' },
          darkColors: { main: '#ef4444', container: '#991b1b', onContainer: '#fee2e2' },
        },
        cancelled: {
          colorName: 'cancelled',
          lightColors: { main: '#ef4444', container: '#fee2e2', onContainer: '#991b1b' },
          darkColors: { main: '#ef4444', container: '#991b1b', onContainer: '#fee2e2' },
        },
        maintenance: {
          colorName: 'maintenance',
          lightColors: { main: '#64748b', container: '#f1f5f9', onContainer: '#334155' },
          darkColors: { main: '#64748b', container: '#334155', onContainer: '#f1f5f9' },
        }
      },
      callbacks: {
        onEventClick: (event) => {
          selectedEvent.value = event;
          isModalOpen.value = true;
        },
        onEventUpdate: async (updatedEvent) => {
          if (!authStore.isAdmin) return;
          const zStart = updatedEvent.start as any;
          const zEnd = updatedEvent.end as any;
          const fmt = (z: any) => `${z.toPlainDate()} ${z.toPlainTime().toString().slice(0, 8)}`;
          
          ui.showConfirm({
            title: 'ยืนยัน',
            message: 'ต้องการเลื่อนเวลาใช่หรือไม่?',
            onConfirm: async () => {
              try {
                await api.patch(`/bookings/${updatedEvent.id}/reschedule`, {
                  start_time: fmt(zStart),
                  end_time: fmt(zEnd)
                });
                ui.showAlert({ title: 'สำเร็จ', message: 'เลื่อนเวลาแล้ว', type: 'success' });
                fetchBookings();
              } catch (e) {
                fetchBookings();
              }
            },
            onCancel: () => fetchBookings()
          });
        }
      }
    });
  } catch (e) {
    console.error('Init error:', e);
  }
};

onMounted(() => {
  roomStore.fetchRooms();
  fetchBookings();
});

const selectRoom = (id: number | '') => {
  selectedRoomId.value = id;
  if (typeof window !== 'undefined') {
    (window.document.activeElement as HTMLElement)?.blur();
  }
};

watch([selectedRoomId, isPendingOnly], () => fetchBookings());
</script>

<template>
  <MainLayout>
    <div class="animate-fade-in min-h-[800px] flex flex-col pb-8 px-4">
      <header class="mb-8 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
        <div>
          <h1 class="text-4xl font-black text-base-content flex items-center gap-3">
            <CalendarIcon class="text-primary" :size="40" />
            ตารางการจอง
          </h1>
          <p class="text-base-content/60 text-sm mt-1 uppercase tracking-widest font-bold">Workspace Overview</p>
        </div>

        <div class="flex flex-wrap items-center gap-4">
          <!-- Room Filter Dropdown (Moved out of Join to prevent clipping) -->
          <div class="dropdown dropdown-bottom">
            <div tabindex="0" role="button" class="btn btn-sm btn-outline btn-ghost font-bold gap-3 rounded-2xl px-6 bg-base-100 shadow-lg border-base-content/10 h-10">
              <span class="opacity-40"><MapPin :size="14" /></span>
              {{ roomStore.rooms.find(r => r.id === selectedRoomId)?.name || 'ทุกห้องประชุม' }}
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" class="opacity-40"><path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </div>
            <ul tabindex="0" class="dropdown-content z-[110] menu p-3 shadow-2xl bg-base-100 rounded-2xl w-72 border border-base-content/10 mt-2 max-h-80 overflow-y-auto premium-scrollbar">
              <li class="menu-title opacity-40 text-[10px] uppercase tracking-widest px-4 py-2">เลือกห้องประชุม</li>
              <li class="mb-1">
                <a @click="selectRoom('')" :class="{ 'active bg-primary/10 text-primary': selectedRoomId === '' }" class="rounded-xl py-3">
                  <div class="flex justify-between w-full items-center">
                    <span>ทุกห้องประชุม</span>
                    <span v-if="selectedRoomId === ''" class="badge badge-primary badge-sm">✓</span>
                  </div>
                </a>
              </li>
              <li v-for="r in roomStore.rooms" :key="r.id" class="mb-1">
                <a @click="selectRoom(r.id)" :class="{ 'active bg-primary/10 text-primary': selectedRoomId === r.id }" class="rounded-xl py-3">
                  <div class="flex justify-between w-full items-center">
                    <span>{{ r.name }}</span>
                    <span v-if="selectedRoomId === r.id" class="badge badge-primary badge-sm">✓</span>
                  </div>
                </a>
              </li>
            </ul>
          </div>

          <div class="join bg-base-100 shadow-lg border border-base-content/5 overflow-hidden rounded-2xl h-10">
            <div class="flex items-center px-4 gap-3 bg-base-200/50 join-item">
              <span class="text-[10px] font-black text-warning uppercase">Pending</span>
              <input type="checkbox" v-model="isPendingOnly" class="toggle toggle-warning toggle-xs" />
            </div>
            <button @click="fetchBookings" class="btn btn-ghost btn-sm join-item px-4 gap-2 border-l border-base-content/5">
              <RefreshCcw :size="16" :class="{ 'animate-spin': loading }" /> Sync
            </button>
          </div>
        </div>
      </header>

      <div class="flex-1 bg-base-100 shadow-2xl border border-base-content/5 overflow-visible">
        <div v-if="calendarApp" class="sx-container min-h-[750px]">
          <ScheduleXCalendar :calendar-app="calendarApp" />
        </div>
      </div>

      <!-- Unified Booking Detail Modal (World Class Consistency) -->
      <BookingDetailModal 
        :is-open="isModalOpen" 
        :booking="selectedEvent?._booking" 
        @close="isModalOpen = false" 
        @refresh="fetchBookings"
      />
    </div>
  </MainLayout>
</template>

<style>
@reference "@/style.css";

.sx-container {
  --sx-color-primary: var(--p);
  --sx-color-on-primary: var(--pc);
  --sx-spacing-padding-1: 0.5rem;
  height: 100%;
}

.sx__month-grid-day {
  transition: background-color 0.2s ease;
}

.sx__month-grid-day:hover {
  background-color: var(--fallback-b2,oklch(var(--b2)/0.3)) !important;
}

.sx__event {
  @apply rounded-lg shadow-sm;
  border: 0 !important;
  transition: transform 0.1s ease;
}

.sx__event:hover {
  transform: scale(1.02);
}

/* Event Status Colors - High Specificity */
.sx__event.event-status-confirmed, .sx__month-grid-event.event-status-confirmed {
  background-color: #22c55e !important;
  color: #ffffff !important;
  border-left: 5px solid #166534 !important;
}

.sx__event.event-status-pending, .sx__month-grid-event.event-status-pending {
  background-color: #f59e0b !important;
  color: #ffffff !important;
  border-left: 5px solid #92400e !important;
}

.sx__event.event-status-rejected, .sx__event.event-status-cancelled, 
.sx__month-grid-event.event-status-rejected, .sx__month-grid-event.event-status-cancelled {
  background-color: #ef4444 !important;
  color: #ffffff !important;
  border-left: 5px solid #991b1b !important;
}

.sx__event.event-status-maintenance, .sx__month-grid-event.event-status-maintenance {
  background-color: #64748b !important;
  color: #ffffff !important;
  border-left: 5px solid #334155 !important;
}
</style>
