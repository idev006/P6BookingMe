<script setup lang="ts">
import { onMounted, ref } from 'vue';
import MainLayout from '../../components/layout/MainLayout.vue';
import api from '../../services/api';
import { useUIStore } from '../../stores/ui';
import { Settings, Save, RefreshCcw, Info, ShieldAlert, ToggleLeft, ToggleRight, Hash, Type } from 'lucide-vue-next';
import { formatDateTime } from '../../utils/format';

const configs = ref<any[]>([]);
const loading = ref(false);
const ui = useUIStore();

const fetchConfigs = async () => {
  loading.value = true;
  try {
    const response = await api.get('/admin/configs');
    configs.value = response.data.data;
  } catch (err) {
    console.error('Failed to fetch configs', err);
  } finally {
    loading.value = false;
  }
};

onMounted(fetchConfigs);

const handleUpdate = async (key: string, value: any) => {
  try {
    await api.patch(`/admin/configs/${key}`, { value });
    ui.showAlert({ title: 'สำเร็จ', message: `อัปเดตค่า ${key} เรียบร้อยแล้ว`, type: 'success' });
    fetchConfigs();
  } catch (err: any) {
    ui.showAlert({ title: 'ผิดพลาด', message: err.response?.data?.detail || 'เกิดข้อผิดพลาด', type: 'error' });
  }
};

const getIcon = (type: string) => {
  switch (type) {
    case 'boolean': return ToggleLeft;
    case 'integer': return Hash;
    default: return Type;
  }
};
</script>

<template>
  <MainLayout>
    <div class="animate-fade-in max-w-5xl mx-auto">
      <header class="mb-10 flex justify-between items-center">
        <div>
          <h1 class="text-3xl font-bold text-base-content mb-2 flex items-center gap-3">
            <Settings class="text-primary" :size="32" />
            ตั้งค่าระบบ (System Settings)
          </h1>
          <p class="text-base-content/60">ปรับแต่งพารามิเตอร์และกฎเกณฑ์การทำงานของแอปพลิเคชัน</p>
        </div>
        <button @click="fetchConfigs" class="btn btn-ghost btn-circle" :disabled="loading">
          <RefreshCcw :class="{ 'animate-spin': loading }" :size="20" />
        </button>
      </header>

      <div class="alert alert-warning mb-8 rounded-2xl shadow-lg border-none">
        <ShieldAlert :size="24" />
        <div>
          <h3 class="font-bold">พื้นที่อันตราย</h3>
          <div class="text-xs opacity-70">การเปลี่ยนแปลงค่าเหล่านี้ส่งผลโดยตรงต่อการทำงานของระบบทั้งหมด โปรดตรวจสอบความถูกต้องก่อนดำเนินการ</div>
        </div>
      </div>

      <div class="grid grid-cols-1 gap-6">
        <div v-for="config in configs" :key="config.id" 
          class="card bg-base-100 shadow-xl border border-base-content/5 hover:border-primary/20 transition-all overflow-hidden group">
          <div class="card-body p-6 md:p-8">
            <div class="flex flex-col md:flex-row md:items-center gap-6">
              <div class="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center text-primary shrink-0">
                <component :is="getIcon(config.type)" :size="24" />
              </div>
              
              <div class="flex-grow">
                <div class="flex items-center gap-2 mb-1">
                  <h3 class="font-mono text-lg font-bold text-primary">{{ config.key }}</h3>
                  <div class="badge badge-sm badge-neutral uppercase font-mono">{{ config.type }}</div>
                </div>
                <p class="text-sm opacity-60">{{ config.description || 'ไม่มีคำอธิบายเพิ่มเติมสำหรับการตั้งค่านี้' }}</p>
              </div>

              <div class="md:w-64 flex gap-2">
                <!-- Boolean Toggle -->
                <template v-if="config.type === 'boolean'">
                  <div class="form-control">
                    <label class="label cursor-pointer gap-4">
                      <span class="label-text opacity-50">{{ config.value ? 'เปิดใช้งาน' : 'ปิดใช้งาน' }}</span>
                      <input 
                        type="checkbox" 
                        class="toggle toggle-primary" 
                        :checked="config.value === 'True' || config.value === true"
                        @change="(e: any) => handleUpdate(config.key, e.target.checked)"
                      />
                    </label>
                  </div>
                </template>

                <!-- Integer/String Input -->
                <template v-else>
                  <div class="join w-full">
                    <input 
                      :type="config.type === 'integer' ? 'number' : 'text'" 
                      v-model="config.value" 
                      class="input input-bordered join-item w-full bg-base-200/50"
                    />
                    <button 
                      @click="handleUpdate(config.key, config.value)" 
                      class="btn btn-primary join-item px-4"
                      title="บันทึก"
                    >
                      <Save :size="18" />
                    </button>
                  </div>
                </template>
              </div>
            </div>
            
            <div class="mt-4 pt-4 border-t border-base-content/5 flex items-center gap-2 text-[10px] opacity-40">
              <Info :size="10" />
              แก้ไขล่าสุดเมื่อ: {{ formatDateTime(config.updated_at) }}
            </div>
          </div>
        </div>

        <div v-if="configs.length === 0 && !loading" class="text-center py-20 text-base-content/30 italic">
          ไม่พบข้อมูลการตั้งค่าระบบ
        </div>
      </div>
    </div>
  </MainLayout>
</template>
