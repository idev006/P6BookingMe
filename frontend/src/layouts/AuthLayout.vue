<script setup lang="ts">
import ThemeSwitcher from '../components/ThemeSwitcher.vue';
</script>

<template>
  <div class="min-h-screen transition-colors duration-300 flex flex-col items-center justify-center p-4 relative">
    <div class="absolute top-8 right-8 z-20">
      <ThemeSwitcher />
    </div>

    <main class="w-full flex justify-center relative z-10">
      <router-view />
    </main>
    
    <div class="mt-8 text-sm opacity-40 relative z-10">
      &copy; 2026 P6BookingMe System
    </div>
  </div>
</template>
