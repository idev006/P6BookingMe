import 'temporal-polyfill/global';
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import router from './router';
import './style.css';
import App from './App.vue';
import { useAuthStore } from './stores/auth';
import { useUIStore } from './stores/ui';

// PrimeVue Imports
import PrimeVue from 'primevue/config';
import Aura from '@primeuix/themes/aura';

async function bootstrap() {
  const app = createApp(App);
  const pinia = createPinia();
  app.use(pinia);
  
  // Configure PrimeVue
  app.use(PrimeVue, {
    theme: {
      preset: Aura,
      options: {
        darkModeSelector: '.dark',
      }
    }
  });

  const ui = useUIStore();
  document.documentElement.setAttribute('data-theme', ui.currentTheme);

  const auth = useAuthStore();
  if (auth.token) {
    try {
      await auth.fetchUser();
    } catch (err) {
      console.error("Auto-login failed:", err);
    }
  }
  
  app.use(router);
  app.mount('#app');
}

bootstrap();
