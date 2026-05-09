import { defineStore } from 'pinia';
import { ref } from 'vue';

export type ModalType = 'info' | 'success' | 'warning' | 'error';

interface ModalOptions {
  title: string;
  message: string;
  type?: ModalType;
  confirmText?: string;
  cancelText?: string;
  onConfirm?: () => void;
  onCancel?: () => void;
}

export const useUIStore = defineStore('ui', () => {
  // Modal State
  const isModalOpen = ref(false);
  const modalOptions = ref<ModalOptions>({
    title: '',
    message: '',
    type: 'info'
  });

  // Theme State
  const currentTheme = ref(localStorage.getItem('p6_theme') || 'night');

  const themes = [
    "light", "dark", "cupcake", "bumblebee", "emerald", "corporate", "synthwave", 
    "retro", "cyberpunk", "valentine", "halloween", "garden", "forest", "aqua", 
    "lofi", "pastel", "fantasy", "wireframe", "black", "luxury", "dracula", 
    "cmyk", "autumn", "business", "acid", "lemonade", "night", "coffee", "winter",
    "dim", "nord", "sunset"
  ];

  const setTheme = (theme: string) => {
    currentTheme.value = theme;
    localStorage.setItem('p6_theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  };

  const showAlert = (options: ModalOptions) => {
    modalOptions.value = {
      ...options,
      type: options.type || 'info',
      confirmText: options.confirmText || 'ตกลง'
    };
    isModalOpen.value = true;
  };

  const showConfirm = (options: ModalOptions) => {
    modalOptions.value = {
      ...options,
      type: options.type || 'warning',
      confirmText: options.confirmText || 'ยืนยัน',
      cancelText: options.cancelText || 'ยกเลิก'
    };
    isModalOpen.value = true;
  };

  const closeModal = () => {
    isModalOpen.value = false;
  };

  return {
    isModalOpen,
    modalOptions,
    currentTheme,
    themes,
    setTheme,
    showAlert,
    showConfirm,
    closeModal
  };
});
