<script setup lang="ts">
import { ref } from 'vue';
import { Upload, Trash2, Star, Check, Loader2 } from 'lucide-vue-next';
import roomService from '../../services/room';
import type { RoomImage } from '../../services/room';
import { getImageUrl } from '../../utils/format';
import { useUIStore } from '../../stores/ui';

const props = defineProps<{
  roomId: number;
  images: RoomImage[];
}>();

const emit = defineEmits(['updated']);
const ui = useUIStore();

const fileInput = ref<HTMLInputElement | null>(null);
const uploading = ref(false);

const handleUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (!target.files?.length) return;

  uploading.value = true;
  try {
    for (const file of target.files) {
      await roomService.uploadImage(props.roomId, file);
    }
    emit('updated');
    ui.showAlert({
      title: 'อัปโหลดสำเร็จ',
      message: 'รูปภาพถูกเพิ่มเข้าไปในระบบเรียบร้อยแล้ว',
      type: 'success'
    });
  } catch (error) {
    ui.showAlert({
      title: 'อัปโหลดไม่สำเร็จ',
      message: String(error),
      type: 'error'
    });
  } finally {
    uploading.value = false;
    if (fileInput.value) fileInput.value.value = '';
  }
};

const setPrimary = async (imageId: number) => {
  try {
    await roomService.setPrimaryImage(props.roomId, imageId);
    emit('updated');
  } catch (error) {
    ui.showAlert({
      title: 'ข้อผิดพลาด',
      message: 'ตั้งค่ารูปหลักไม่สำเร็จ',
      type: 'error'
    });
  }
};

const deleteImage = async (imageId: number) => {
  ui.showConfirm({
    title: 'ยืนยันการลบ',
    message: 'คุณต้องการลบรูปภาพนี้ใช่หรือไม่?',
    type: 'warning',
    onConfirm: async () => {
      try {
        await roomService.deleteImage(props.roomId, imageId);
        emit('updated');
      } catch (error) {
        ui.showAlert({
          title: 'ข้อผิดพลาด',
          message: 'ลบไม่สำเร็จ',
          type: 'error'
        });
      }
    }
  });
};
</script>

<template>
  <div class="space-y-4">
    <h3 class="text-lg font-bold text-white flex items-center gap-2">
      <Building2 :size="20" class="text-indigo-400" />
      จัดการรูปภาพห้องประชุม
    </h3>
    
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
      <div v-for="img in images" :key="img.id" 
        class="group relative aspect-video rounded-xl overflow-hidden border-2 transition-all"
        :class="img.is_primary ? 'border-indigo-500 shadow-lg shadow-indigo-500/20' : 'border-white/5 shadow-md hover:border-white/20'"
      >
        <img :src="getImageUrl(img.image_path)" alt="Room" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
        
        <!-- Overlays -->
        <div class="absolute inset-0 bg-slate-950/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <button v-if="!img.is_primary" @click="setPrimary(img.id)" class="btn btn-circle btn-sm bg-white text-indigo-600 hover:bg-indigo-50 border-none shadow-lg" title="ตั้งเป็นรูปหลัก">
            <Star :size="16" />
          </button>
          <button @click="deleteImage(img.id)" class="btn btn-circle btn-sm bg-red-600 text-white hover:bg-red-500 border-none shadow-lg" title="ลบรูปภาพ">
            <Trash2 :size="16" />
          </button>
        </div>

        <div v-if="img.is_primary" class="absolute top-2 left-2 badge badge-primary gap-1 border-none shadow-md font-bold text-[10px]">
          <Check :size="10" /> รูปหลัก
        </div>
      </div>

      <!-- Add Image Placeholder -->
      <div 
        @click="fileInput?.click()" 
        class="aspect-video rounded-xl border-2 border-dashed border-white/10 hover:border-indigo-500/50 hover:bg-white/5 flex flex-col items-center justify-center cursor-pointer transition-all gap-2 text-slate-500 hover:text-indigo-400 group"
      >
        <input ref="fileInput" type="file" multiple accept="image/*" class="hidden" @change="handleUpload" />
        <template v-if="uploading">
          <Loader2 :size="24" class="animate-spin text-indigo-500" />
          <span class="text-xs font-medium">กำลังอัปโหลด...</span>
        </template>
        <template v-else>
          <div class="p-3 rounded-full bg-slate-900 group-hover:bg-indigo-500/10 transition-colors flex items-center justify-center">
            <Upload :size="24" />
          </div>
          <span class="text-xs font-bold uppercase tracking-wider">เพิ่มรูปภาพ</span>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Scoped styles removed, using Tailwind/DaisyUI */
</style>
