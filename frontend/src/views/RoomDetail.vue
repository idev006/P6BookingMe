<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ChevronLeft, Users, Building2, CheckCircle2, CalendarDays } from 'lucide-vue-next';
import MainLayout from '../components/layout/MainLayout.vue';
import { useRoomStore } from '../stores/room';
import { getImageUrl } from '../utils/format';

const route = useRoute();
const router = useRouter();
const roomStore = useRoomStore();
const activeImage = ref('');

const fetchRoom = async () => {
  const id = parseInt(route.params.id as string);
  await roomStore.fetchRoomDetail(id);
};

watch(() => roomStore.selectedRoom, (newRoom) => {
  if (newRoom) {
    const primary = newRoom.images.find((img: any) => img.is_primary);
    activeImage.value = primary ? primary.image_path : (newRoom.images[0]?.image_path || '');
  }
}, { immediate: true });

onMounted(fetchRoom);
</script>

<template>
  <MainLayout>
    <div class="max-w-6xl mx-auto">
      <button @click="router.back()" class="btn btn-ghost gap-2 mb-8">
        <ChevronLeft :size="20" /> กลับ
      </button>

      <div v-if="roomStore.loading" class="flex flex-col gap-8">
        <div class="h-96 bg-base-100 animate-pulse rounded-3xl"></div>
        <div class="h-48 bg-base-100 animate-pulse rounded-3xl"></div>
      </div>

      <div v-else-if="roomStore.selectedRoom" class="grid grid-cols-1 lg:grid-cols-2 gap-10 animate-fade-in">
        <!-- Media Section -->
        <div class="flex flex-col gap-6">
          <div class="aspect-video card bg-base-100 shadow-xl overflow-hidden group">
            <img v-if="activeImage" :src="getImageUrl(activeImage)" alt="Room" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
            <div v-else class="w-full h-full flex items-center justify-center bg-base-200 text-base-content/20">
              <Building2 :size="80" />
            </div>
          </div>
          
          <div class="flex gap-4 overflow-x-auto pb-2 scrollbar-hide">
            <div 
              v-for="img in roomStore.selectedRoom.images" 
              :key="img.id" 
              class="w-24 h-16 rounded-xl overflow-hidden cursor-pointer border-2 transition-all shrink-0" 
              :class="activeImage === img.image_path ? 'border-primary scale-105' : 'border-transparent opacity-60 hover:opacity-100'"
              @click="activeImage = img.image_path"
            >
              <img :src="getImageUrl(img.image_path)" alt="Thumb" class="w-full h-full object-cover" />
            </div>
          </div>
        </div>

        <!-- Info Section -->
        <div class="flex flex-col gap-8">
          <div class="card bg-base-100 shadow-xl p-8 border border-base-content/5">
            <div class="flex justify-between items-start mb-6">
              <h1 class="text-4xl font-bold text-base-content">{{ roomStore.selectedRoom.name }}</h1>
              <div :class="['badge badge-lg gap-2 font-bold', roomStore.selectedRoom.status === 'active' ? 'badge-success' : 'badge-error']">
                {{ roomStore.selectedRoom.status === 'active' ? 'ว่าง' : 'ปิดปรับปรุง' }}
              </div>
            </div>

            <div class="grid grid-cols-2 gap-6 mb-8">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                  <Users :size="20" />
                </div>
                <div>
                  <div class="text-xs text-base-content/50 uppercase font-bold tracking-wider">ความจุ</div>
                  <div class="font-semibold">{{ roomStore.selectedRoom.capacity }} คน</div>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                  <Building2 :size="20" />
                </div>
                <div>
                  <div class="text-xs text-base-content/50 uppercase font-bold tracking-wider">อาคาร/ชั้น</div>
                  <div class="font-semibold">{{ roomStore.selectedRoom.building || '-' }} / {{ roomStore.selectedRoom.floor ? `ชั้น ${roomStore.selectedRoom.floor}` : '-' }}</div>
                </div>
              </div>
            </div>

            <div class="divider"></div>

            <div class="mb-8">
              <h3 class="text-lg font-bold mb-3">รายละเอียด</h3>
              <p class="text-base-content/70 leading-relaxed">{{ roomStore.selectedRoom.description || 'ไม่มีรายละเอียดเพิ่มเติม' }}</p>
            </div>

            <div class="mb-10">
              <h3 class="text-lg font-bold mb-4">อุปกรณ์ที่มีให้</h3>
              <div class="flex flex-wrap gap-3">
                <div v-for="eq in roomStore.selectedRoom.equipment" :key="eq.id" class="badge badge-lg bg-base-200 border-none py-4 px-4 gap-2">
                  <CheckCircle2 :size="16" class="text-primary" />
                  {{ eq.name }}
                </div>
                <div v-if="roomStore.selectedRoom.equipment.length === 0" class="text-base-content/30 italic">ไม่มีข้อมูลอุปกรณ์</div>
              </div>
            </div>

            <button 
              class="btn btn-primary w-full btn-lg font-bold text-lg shadow-xl" 
              :disabled="roomStore.selectedRoom.status !== 'active'"
              @click="router.push(`/rooms/${roomStore.selectedRoom.id}/book`)"
            >
              <CalendarDays :size="22" />
              จองห้องนี้
            </button>
            <p v-if="roomStore.selectedRoom.status !== 'active'" class="text-center text-error mt-4 text-sm font-medium italic">
              ขณะนี้ห้องนี้ไม่เปิดให้บริการ
            </p>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>
