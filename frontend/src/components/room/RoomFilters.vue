<script setup lang="ts">
import { Filter } from 'lucide-vue-next';

defineProps<{
  buildings: string[];
  modelValue: {
    building: string;
    minCapacity: number | null;
  }
}>();

const emit = defineEmits(['update:modelValue', 'clear']);

const updateFilter = (key: string, value: any) => {
  emit('update:modelValue', {
    ...props.modelValue,
    [key]: value
  });
};

// We need to use props to get current values, but defineProps returns a readonly object.
// Let's simplify and use the v-model approach if possible, but for a group of filters, 
// sometimes it's easier to just pass the ref.
</script>

<template>
  <aside class="card bg-base-100 shadow-xl p-6 h-fit sticky top-24 border border-base-content/5">
    <div class="flex items-center gap-2 font-bold text-lg mb-6 text-base-content border-b border-base-content/10 pb-4">
      <Filter :size="18" />
      <span>ตัวกรอง</span>
    </div>

    <div class="form-control w-full mb-6">
      <label class="label"><span class="label-text">อาคาร</span></label>
      <select 
        :value="modelValue.building" 
        @change="(e: any) => $emit('update:modelValue', { ...modelValue, building: e.target.value })"
        class="select select-bordered w-full"
      >
        <option value="">ทั้งหมด</option>
        <option v-for="b in buildings" :key="b" :value="b">{{ b }}</option>
      </select>
    </div>

    <div class="form-control w-full mb-6">
      <label class="label"><span class="label-text">ความจุขั้นต่ำ (คน)</span></label>
      <input 
        :value="modelValue.minCapacity" 
        @input="(e: any) => $emit('update:modelValue', { ...modelValue, minCapacity: e.target.value ? parseInt(e.target.value) : null })"
        type="number" 
        placeholder="เช่น 5" 
        class="input input-bordered w-full" 
        min="0" 
      />
    </div>

    <div class="form-control mb-6">
      <label class="label cursor-pointer justify-start gap-3">
        <input type="checkbox" class="checkbox checkbox-primary" />
        <span class="label-text">โปรเจคเตอร์</span>
      </label>
      <label class="label cursor-pointer justify-start gap-3">
        <input type="checkbox" class="checkbox checkbox-primary" />
        <span class="label-text">ไวท์บอร์ด</span>
      </label>
    </div>

    <button @click="$emit('clear')" class="btn btn-outline btn-sm w-full">
      ล้างตัวกรอง
    </button>
  </aside>
</template>
