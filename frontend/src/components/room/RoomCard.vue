<script setup lang="ts">
import { Users, MapPin, Building2, ChevronRight } from 'lucide-vue-next';
import type { Room } from '../../services/room';
import { getImageUrl } from '../../utils/format';

defineProps<{
  room: Room;
  viewMode: 'grid' | 'list';
}>();

const emit = defineEmits(['view-detail']);

const getPrimaryImage = (room: Room) => {
  const primary = room.images.find(img => img.is_primary);
  return primary ? getImageUrl(primary.image_path) : null;
};
</script>

<template>
  <div 
    class="card bg-base-100 shadow-xl overflow-hidden cursor-pointer transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl border border-base-content/5 group"
    :class="{ 'flex-row h-48': viewMode === 'list' }"
    @click="emit('view-detail', room.id)"
  >
    <figure :class="viewMode === 'grid' ? 'h-48' : 'w-72 h-full'">
      <img 
        v-if="getPrimaryImage(room)" 
        :src="getPrimaryImage(room)!" 
        alt="Room Image" 
        class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
      />
      <div v-else class="w-full h-full flex items-center justify-center bg-base-200 text-base-content/20">
        <Building2 :size="48" />
      </div>
      <div class="absolute top-3 right-3 badge badge-neutral bg-black/60 backdrop-blur-md border-white/10 gap-1.5 py-3">
        <Users :size="12" />
        <span class="text-xs font-bold">{{ room.capacity }} คน</span>
      </div>
    </figure>
    
    <div class="card-body p-5">
      <div class="flex justify-between items-start">
        <h3 class="card-title text-base-content">{{ room.name }}</h3>
        <div 
          class="badge badge-xs" 
          :class="room.status === 'active' ? 'badge-success shadow-[0_0_8px_rgba(74,222,128,0.4)]' : 'badge-error'"
        ></div>
      </div>
      
      <div class="flex flex-col gap-1.5 mt-2">
        <div class="flex items-center gap-2 text-base-content/50 text-sm">
          <Building2 :size="14" />
          <span>{{ room.building || 'ไม่ระบุอาคาร' }} {{ room.floor ? `(ชั้น ${room.floor})` : '' }}</span>
        </div>
        <div class="flex items-center gap-2 text-base-content/50 text-sm">
          <MapPin :size="14" />
          <span>{{ room.location }}</span>
        </div>
      </div>

      <div class="card-actions justify-between items-center mt-4 pt-4 border-t border-base-content/5">
        <div class="flex items-center gap-1">
          <span v-for="eq in room.equipment.slice(0, 3)" :key="eq.id" class="w-1.5 h-1.5 rounded-full bg-primary"></span>
          <span v-if="room.equipment.length > 3" class="text-[10px] text-base-content/40 ml-1">+{{ room.equipment.length - 3 }}</span>
        </div>
        <button class="btn btn-ghost btn-xs text-primary font-bold gap-1 group-hover:gap-2 transition-all">
          ดูรายละเอียด <ChevronRight :size="14" />
        </button>
      </div>
    </div>
  </div>
</template>
