<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import MainLayout from '../components/layout/MainLayout.vue';
import { useAuthStore } from '../stores/auth';
import { useUIStore } from '../stores/ui';
import api from '../services/api';
import { getImageUrl } from '../utils/format';
import { User as UserIcon, Phone, Mail, BadgeCheck, Camera, Save, Loader2 } from 'lucide-vue-next';

const auth = useAuthStore();
const ui = useUIStore();
const loading = ref(false);
const uploading = ref(false);

const form = reactive({
  full_name: '',
  phone: ''
});

onMounted(() => {
  if (auth.user) {
    form.full_name = auth.user.full_name;
    form.phone = auth.user.phone || '';
  }
});

const handleUpdate = async () => {
  loading.value = true;
  try {
    await api.patch('/users/me/', form);
    await auth.fetchUser(); // Refresh local data
    ui.showAlert({ title: 'สำเร็จ', message: 'อัปเดตข้อมูลส่วนตัวเรียบร้อยแล้ว', type: 'success' });
  } catch (err: any) {
    ui.showAlert({ title: 'ผิดพลาด', message: err.response?.data?.detail || 'เกิดข้อผิดพลาด', type: 'error' });
  } finally {
    loading.value = false;
  }
};

const handleAvatarUpload = async (event: any) => {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  uploading.value = true;
  try {
    await api.post('/users/me/avatar/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    await auth.fetchUser();
    ui.showAlert({ title: 'สำเร็จ', message: 'อัปโหลดรูปโปรไฟล์เรียบร้อยแล้ว', type: 'success' });
  } catch (err: any) {
    ui.showAlert({ title: 'ผิดพลาด', message: err.response?.data?.detail || 'อัปโหลดไม่สำเร็จ', type: 'error' });
  } finally {
    uploading.value = false;
  }
};
</script>

<template>
  <MainLayout>
    <div class="max-w-3xl mx-auto animate-fade-in">
      <header class="mb-10">
        <h1 class="text-3xl font-bold text-base-content mb-2">ข้อมูลส่วนตัว</h1>
        <p class="text-base-content/60">จัดการข้อมูลพื้นฐานและการตั้งค่าบัญชีของคุณ</p>
      </header>

      <div class="grid grid-cols-1 md:grid-cols-[280px_1fr] gap-8">
        <!-- Avatar Section -->
        <div class="flex flex-col items-center gap-6">
          <div class="relative group">
            <div class="w-48 h-48 rounded-3xl bg-base-100 shadow-2xl border-4 border-primary/20 overflow-hidden">
              <img v-if="auth.user?.avatar_path" :src="getImageUrl(auth.user.avatar_path)" class="w-full h-full object-cover" />
              <div v-else class="w-full h-full flex items-center justify-center bg-base-200 text-base-content/20">
                <UserIcon :size="80" />
              </div>
            </div>
            
            <label class="absolute -bottom-4 -right-4 btn btn-primary btn-circle shadow-xl cursor-pointer">
              <Camera v-if="!uploading" :size="20" />
              <Loader2 v-else class="animate-spin" :size="20" />
              <input type="file" class="hidden" accept="image/*" @change="handleAvatarUpload" :disabled="uploading" />
            </label>
          </div>

          <div class="text-center">
            <div class="badge badge-primary badge-lg font-bold py-4 uppercase tracking-widest">{{ auth.user?.role }}</div>
            <p class="mt-4 text-xs opacity-40">เข้าร่วมเมื่อ: {{ auth.user?.created_at ? new Date(auth.user.created_at).toLocaleDateString() : 'N/A' }}</p>
          </div>
        </div>

        <!-- Form Section -->
        <div class="card bg-base-100 shadow-xl border border-base-content/5">
          <div class="card-body gap-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="form-control">
                <label class="label"><span class="label-text font-bold">ชื่อ-นามสกุล</span></label>
                <div class="input-group flex items-center bg-base-200/50 rounded-xl px-4">
                  <UserIcon :size="18" class="opacity-40" />
                  <input v-model="form.full_name" type="text" class="input bg-transparent border-none w-full focus:outline-none" />
                </div>
              </div>
              <div class="form-control">
                <label class="label"><span class="label-text font-bold">เบอร์โทรศัพท์</span></label>
                <div class="input-group flex items-center bg-base-200/50 rounded-xl px-4">
                  <Phone :size="18" class="opacity-40" />
                  <input v-model="form.phone" type="text" class="input bg-transparent border-none w-full focus:outline-none" />
                </div>
              </div>
            </div>

            <div class="divider opacity-5 my-0"></div>

            <div class="space-y-4">
              <div class="flex items-center justify-between p-4 bg-base-200/30 rounded-2xl">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-xl bg-base-300 flex items-center justify-center opacity-40">
                    <Mail :size="20" />
                  </div>
                  <div>
                    <div class="text-[10px] uppercase font-bold opacity-40">Email (ห้ามเปลี่ยน)</div>
                    <div class="font-medium">{{ auth.user?.email }}</div>
                  </div>
                </div>
                <BadgeCheck class="text-success" :size="20" />
              </div>

              <div class="flex items-center justify-between p-4 bg-base-200/30 rounded-2xl">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-xl bg-base-300 flex items-center justify-center opacity-40">
                    <BadgeCheck :size="20" />
                  </div>
                  <div>
                    <div class="text-[10px] uppercase font-bold opacity-40">รหัสพนักงาน (ห้ามเปลี่ยน)</div>
                    <div class="font-medium">{{ auth.user?.employee_code }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="card-actions justify-end mt-4">
              <button @click="handleUpdate" class="btn btn-primary px-10 gap-2 shadow-lg shadow-primary/20" :disabled="loading">
                <Save v-if="!loading" :size="20" />
                <Loader2 v-else class="animate-spin" :size="20" />
                บันทึกการเปลี่ยนแปลง
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>
