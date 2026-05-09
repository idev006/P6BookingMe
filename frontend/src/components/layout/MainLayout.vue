<script setup lang="ts">
import Navbar from '../common/Navbar.vue';
</script>

<template>
  <div class="min-h-screen transition-colors duration-300 flex flex-col">
    <!-- Navbar -->
    <Navbar />

    <!-- Main Content -->
    <main class="flex-grow container mx-auto p-4 md:p-8 relative z-10">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="footer footer-center p-10 bg-base-100 text-base-content rounded mt-auto border-t border-base-content/5 relative z-10">
      <nav class="grid grid-flow-col gap-4">
        <a class="link link-hover">About us</a>
        <a class="link link-hover">Contact</a>
        <a class="link link-hover">Privacy Policy</a>
      </nav> 
      <aside>
        <p>Copyright © 2026 - All right reserved by P6BookingMe</p>
      </aside>
    </footer>
  </div>
</template>
