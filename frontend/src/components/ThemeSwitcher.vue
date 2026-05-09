<script setup lang="ts">
import { useUIStore } from '../stores/ui';
const ui = useUIStore();
</script>

<template>
  <div class="dropdown dropdown-end">
    <div tabindex="0" role="button" class="btn btn-ghost m-1">
      <svg width="20" height="20" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="inline-block h-5 w-5 stroke-current"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"></path></svg>
      <span class="hidden md:inline">Theme</span>
      <svg width="12px" height="12px" class="h-2 w-2 fill-current opacity-60 inline-block" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2048 2048"><path d="M1799 346l128 128-896 896-896-896 128-128 768 768 768-768z"></path></svg>
    </div>
    <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow-2xl bg-base-200 rounded-box w-52 max-h-96 overflow-y-auto mt-4 border border-base-content/10">
      <li v-for="theme in ui.themes" :key="theme">
        <input 
          type="radio" 
          name="theme-dropdown" 
          class="theme-controller btn btn-sm btn-block btn-ghost justify-start" 
          :aria-label="theme" 
          :value="theme"
          :checked="ui.currentTheme === theme"
          @change="ui.setTheme(theme)"
        />
      </li>
    </ul>
  </div>
</template>
