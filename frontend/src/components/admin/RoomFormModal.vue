<script setup lang="ts">
import { ref, watch } from 'vue';
import { X, Save, Plus, Trash2 } from 'lucide-vue-next';
import roomService from '../../services/room';
import type { Room, RoomCreateData } from '../../services/room';

const props = defineProps<{
  show: boolean;
  room?: Room | null;
}>();

const emit = defineEmits(['close', 'saved']);

const form = ref<RoomCreateData>({
  name: '',
  capacity: 10,
  location: '',
  building: '',
  floor: '',
  description: '',
  equipment: []
});

const equipmentInput = ref('');
const loading = ref(false);
const error = ref('');

watch(() => props.room, (newRoom) => {
  if (newRoom) {
    form.value = {
      name: newRoom.name,
      capacity: newRoom.capacity,
      location: newRoom.location,
      building: newRoom.building || '',
      floor: newRoom.floor || '',
      description: newRoom.description || '',
      equipment: newRoom.equipment.map(e => e.name)
    };
  } else {
    form.value = {
      name: '',
      capacity: 10,
      location: '',
      building: '',
      floor: '',
      description: '',
      equipment: []
    };
  }
}, { immediate: true });

const addEquipment = () => {
  if (equipmentInput.value.trim()) {
    form.value.equipment?.push(equipmentInput.value.trim());
    equipmentInput.value = '';
  }
};

const removeEquipment = (index: number) => {
  form.value.equipment?.splice(index, 1);
};

const submit = async () => {
  loading.value = true;
  error.value = '';
  try {
    if (props.room) {
      await roomService.updateRoom(props.room.id, form.value);
    } else {
      await roomService.createRoom(form.value);
    }
    emit('saved');
    emit('close');
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'เกิดข้อผิดพลาดในการบันทึกข้อมูล';
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div v-if="show" class="modal-overlay" @click.self="emit('close')">
    <div class="glass-card modal-content">
      <div class="modal-header">
        <h2>{{ room ? 'แก้ไขห้องประชุม' : 'เพิ่มห้องประชุมใหม่' }}</h2>
        <button class="btn-close" @click="emit('close')"><X :size="20" /></button>
      </div>

      <form @submit.prevent="submit" class="modal-body">
        <div v-if="error" class="error-msg">{{ error }}</div>

        <div class="form-row">
          <div class="form-group">
            <label>ชื่อห้องประชุม *</label>
            <input v-model="form.name" type="text" required placeholder="เช่น Meeting Room 1" />
          </div>
          <div class="form-group sm">
            <label>ความจุ (คน) *</label>
            <input v-model.number="form.capacity" type="number" required min="1" />
          </div>
        </div>

        <div class="form-group">
          <label>สถานที่ / ที่ตั้ง *</label>
          <input v-model="form.location" type="text" required placeholder="เช่น ฝั่งตะวันออก" />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>อาคาร</label>
            <input v-model="form.building" type="text" placeholder="เช่น อาคาร A" />
          </div>
          <div class="form-group sm">
            <label>ชั้น</label>
            <input v-model="form.floor" type="text" placeholder="เช่น 4" />
          </div>
        </div>

        <div class="form-group">
          <label>รายละเอียดเพิ่มเติม</label>
          <textarea v-model="form.description" rows="3" placeholder="บรรยายรายละเอียดของห้อง..."></textarea>
        </div>

        <div class="form-group">
          <label>อุปกรณ์ภายในห้อง</label>
          <div class="equipment-input">
            <input v-model="equipmentInput" @keydown.enter.prevent="addEquipment" type="text" placeholder="พิมพ์ชื่ออุปกรณ์แล้วกด Enter" />
            <button type="button" @click="addEquipment" class="btn-add"><Plus :size="18" /></button>
          </div>
          <div class="equipment-tags">
            <span v-for="(item, index) in form.equipment" :key="index" class="tag">
              {{ item }}
              <button type="button" @click="removeEquipment(index)"><X :size="12" /></button>
            </span>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn-secondary" @click="emit('close')">ยกเลิก</button>
          <button type="submit" class="btn-primary" :disabled="loading">
            <Save :size="18" />
            {{ loading ? 'กำลังบันทึก...' : 'บันทึกข้อมูล' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 0;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  color: white;
  font-size: 1.5rem;
}

.modal-body {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-row {
  display: flex;
  gap: 1rem;
}

.form-group.sm {
  flex: 0 0 120px;
}

label {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

input, textarea {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 0.75rem;
  color: white;
  outline: none;
  transition: all 0.2s;
}

input:focus, textarea:focus {
  border-color: #6366f1;
  background: rgba(255, 255, 255, 0.08);
}

.equipment-input {
  display: flex;
  gap: 0.5rem;
}

.equipment-input input {
  flex: 1;
}

.btn-add {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  width: 40px;
  border-radius: 8px;
  cursor: pointer;
}

.equipment-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.tag {
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tag button {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  display: flex;
  padding: 0;
}

.modal-footer {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.05);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  cursor: pointer;
}

.btn-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
}

.error-msg {
  background: rgba(244, 67, 54, 0.1);
  color: #f87171;
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  border: 1px solid rgba(244, 67, 54, 0.2);
}
</style>
