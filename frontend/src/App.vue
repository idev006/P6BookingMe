<script setup lang="ts">
import { useUIStore } from './stores/ui';
const ui = useUIStore();

const handleConfirm = () => {
  if (ui.modalOptions.onConfirm) ui.modalOptions.onConfirm();
  ui.closeModal();
};

const handleCancel = () => {
  if (ui.modalOptions.onCancel) ui.modalOptions.onCancel();
  ui.closeModal();
};
</script>

<template>
  <div class="app-container">
    <router-view />

    <!-- Global Modal (DaisyUI) -->
    <dialog class="modal" :class="{ 'modal-open': ui.isModalOpen }">
      <div class="modal-box border border-base-content/10 bg-base-100 shadow-2xl">
        <h3 class="font-bold text-2xl mb-4" :class="{
          'text-info': ui.modalOptions.type === 'info',
          'text-success': ui.modalOptions.type === 'success',
          'text-warning': ui.modalOptions.type === 'warning',
          'text-error': ui.modalOptions.type === 'error'
        }">
          {{ ui.modalOptions.title }}
        </h3>
        <p class="py-4 text-base-content/80 text-lg">{{ ui.modalOptions.message }}</p>
        <div class="modal-action gap-2">
          <button v-if="ui.modalOptions.cancelText" class="btn btn-ghost" @click="handleCancel">
            {{ ui.modalOptions.cancelText }}
          </button>
          <button class="btn px-8" 
            :class="{
              'btn-info': ui.modalOptions.type === 'info',
              'btn-success': ui.modalOptions.type === 'success',
              'btn-warning': ui.modalOptions.type === 'warning',
              'btn-error': ui.modalOptions.type === 'error'
            }"
            @click="handleConfirm">
            {{ ui.modalOptions.confirmText }}
          </button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop" @click="ui.closeModal">
        <button>close</button>
      </form>
    </dialog>
  </div>
</template>

<style>
/* Global scrollbar styling */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: currentColor;
  opacity: 0.2;
  border-radius: 10px;
}
</style>
