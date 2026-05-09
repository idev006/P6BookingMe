<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { Search, LayoutGrid, LayoutList } from 'lucide-vue-next';
import MainLayout from '../components/layout/MainLayout.vue';
import RoomCard from '../components/room/RoomCard.vue';
import RoomFilters from '../components/room/RoomFilters.vue';
import { useRoomStore } from '../stores/room';

const roomStore = useRoomStore();
const viewMode = ref<'grid' | 'list'>('grid');

// Filters
const searchQuery = ref('');
let filters = ref({
  building: '',
  minCapacity: null as number | null
});

const filteredRooms = computed(() => {
  return roomStore.rooms.filter(room => {
    const matchesSearch = room.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                          room.location.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesBuilding = !filters.value.building || room.building === filters.value.building;
    const matchesCapacity = !filters.value.minCapacity || room.capacity >= filters.value.minCapacity;
    
    return matchesSearch && matchesBuilding && matchesCapacity;
  });
});

const uniqueBuildings = computed(() => {
  const buildings = roomStore.rooms.map(r => r.building).filter(Boolean) as string[];
  return [...new Set(buildings)];
});

const clearFilters = () => {
  searchQuery.value = '';
  filters.value.building = '';
  filters.value.minCapacity = null;
};

onMounted(() => {
  roomStore.fetchRooms({ status: 'active' });
});
</script>

<template>
  <MainLayout>
    <div class="max-w-7xl mx-auto">
      <header class="mb-10 animate-fade-in">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <h1 class="text-4xl font-bold text-base-content mb-2">ค้นหาห้องประชุม</h1>
            <p class="text-base-content/60">ค้นหาและเลือกห้องที่เหมาะสมกับการประชุมของคุณ</p>
          </div>
          
          <div class="join w-full md:w-96 shadow-xl">
            <input v-model="searchQuery" class="input input-bordered join-item w-full bg-base-100" placeholder="ชื่อห้อง หรือสถานที่..."/>
            <button class="btn btn-primary join-item">
              <Search :size="20" />
            </button>
          </div>
        </div>
      </header>

      <div class="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-8">
        <!-- Sidebar Filters Component -->
        <RoomFilters 
          v-model="filters" 
          :buildings="uniqueBuildings" 
          @clear="clearFilters"
        />

        <!-- Main Results -->
        <section class="animate-fade-in" style="animation-delay: 0.1s">
          <div class="flex justify-between items-center mb-6">
            <span class="text-base-content/60 font-medium">พบ {{ filteredRooms.length }} ห้อง</span>
            <div class="join bg-base-100 border border-base-content/10 p-1">
              <button @click="viewMode = 'grid'" :class="['btn btn-sm join-item border-none', viewMode === 'grid' ? 'btn-primary' : 'btn-ghost']">
                <LayoutGrid :size="18" />
              </button>
              <button @click="viewMode = 'list'" :class="['btn btn-sm join-item border-none', viewMode === 'list' ? 'btn-primary' : 'btn-ghost']">
                <LayoutList :size="18" />
              </button>
            </div>
          </div>

          <div v-if="roomStore.loading" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            <div v-for="i in 6" :key="i" class="h-80 bg-base-100 rounded-3xl animate-pulse"></div>
          </div>

          <div v-else-if="filteredRooms.length > 0" :class="['grid gap-6', viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 xl:grid-cols-3' : 'grid-cols-1']">
            <RoomCard 
              v-for="room in filteredRooms" 
              :key="room.id" 
              :room="room" 
              :view-mode="viewMode"
              @view-detail="(id) => $router.push(`/rooms/${id}`)"
            />
          </div>

          <div v-else class="card bg-base-100 py-20 text-center flex flex-col items-center shadow-xl">
            <div class="w-20 h-20 bg-base-200 rounded-full flex items-center justify-center mb-6 text-base-content/20">
              <Search :size="40" />
            </div>
            <h3 class="text-2xl font-bold text-base-content mb-2">ไม่พบห้องประชุมที่ตรงตามเงื่อนไข</h3>
            <p class="text-base-content/50 mb-8">ลองปรับเปลี่ยนคำค้นหาหรือตัวกรองใหม่อีกครั้ง</p>
          </div>
        </section>
      </div>
    </div>
  </MainLayout>
</template>
