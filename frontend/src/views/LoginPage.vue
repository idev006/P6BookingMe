<script setup lang="ts">
import { reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const router = useRouter();

const form = reactive({
  email: '',
  password: '',
});

const handleLogin = async () => {
  try {
    await auth.login(form);
    router.push('/dashboard');
  } catch (err) {
    // Error handled by store
  }
};
</script>

<template>
  <div class="card bg-base-100 shadow-2xl w-full max-w-md animate-fade-in border border-base-content/5">
    <div class="card-body gap-6">
      <div class="text-center">
        <h1 class="text-4xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent mb-2">Welcome Back</h1>
        <p class="text-base-content/60">Login to your P6BookingMe account</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-5">
        <div class="space-y-2">
          <label class="text-xs font-black uppercase tracking-widest opacity-40 ml-1">Email Address</label>
          <input 
            v-model="form.email" 
            type="email" 
            placeholder="name@company.com" 
            class="input input-bordered w-full bg-base-200/50 border-base-content/5 focus:border-primary/30 transition-all" 
            required 
          />
        </div>
        
        <div class="space-y-2">
          <label class="text-xs font-black uppercase tracking-widest opacity-40 ml-1">Password</label>
          <input 
            v-model="form.password" 
            type="password" 
            placeholder="••••••••" 
            class="input input-bordered w-full bg-base-200/50 border-base-content/5 focus:border-primary/30 transition-all" 
            required 
          />
        </div>

        <div v-if="auth.error" class="alert alert-error text-xs py-3 shadow-lg shadow-error/10">
          <span class="font-bold uppercase tracking-tight">{{ auth.error }}</span>
        </div>

        <button type="submit" class="btn btn-primary btn-block h-14 text-sm font-black uppercase tracking-[0.2em] shadow-xl shadow-primary/25 group overflow-hidden" :disabled="auth.loading">
          <span v-if="!auth.loading" class="group-hover:scale-110 transition-transform">Sign In Securely</span>
          <span v-else class="loading loading-spinner"></span>
        </button>
      </form>

      <div class="text-center text-[10px] font-bold uppercase tracking-widest opacity-30 mt-4">
        New to the platform? 
        <router-link to="/register" class="text-primary hover:underline">Create account</router-link>
      </div>
    </div>
  </div>
</template>
