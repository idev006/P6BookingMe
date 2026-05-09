<script setup lang="ts">
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const router = useRouter();
const success = ref(false);
const password_confirm = ref('');
const validationError = ref('');

const form = reactive({
  email: '',
  password: '',
  full_name: '',
  employee_code: '',
  department: '',
  phone: '',
});

const handleRegister = async () => {
  if (form.password !== password_confirm.value) {
    validationError.value = 'รหัสผ่านไม่ตรงกัน';
    return;
  }
  validationError.value = '';
  
  try {
    await auth.register(form);
    success.value = true;
  } catch (err) {
    // Error handled by store
  }
};
</script>

<template>
  <div class="card bg-base-100 shadow-2xl w-full max-w-2xl animate-fade-in border border-base-content/5">
    <div class="card-body gap-6">
      <div v-if="!success">
        <div class="text-center mb-6">
          <h1 class="text-4xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent mb-2">Join Us</h1>
          <p class="text-base-content/60">Create your employee account</p>
        </div>

        <form @submit.prevent="handleRegister" class="space-y-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-2">
              <label class="text-[10px] font-black uppercase tracking-widest opacity-40 ml-1">Full Name</label>
              <input v-model="form.full_name" type="text" placeholder="John Doe" class="input input-bordered w-full bg-base-200/50 border-base-content/5 focus:border-primary/30 transition-all" required />
            </div>
            <div class="space-y-2">
              <label class="text-[10px] font-black uppercase tracking-widest opacity-40 ml-1">Employee Code</label>
              <input v-model="form.employee_code" type="text" placeholder="EMP001" class="input input-bordered w-full bg-base-200/50 border-base-content/5 focus:border-primary/30 transition-all" required />
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-[10px] font-black uppercase tracking-widest opacity-40 ml-1">Email Address</label>
            <input v-model="form.email" type="email" placeholder="name@company.com" class="input input-bordered w-full bg-base-200/50 border-base-content/5 focus:border-primary/30 transition-all" required />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-2">
              <label class="text-[10px] font-black uppercase tracking-widest opacity-40 ml-1">Department</label>
              <input v-model="form.department" type="text" placeholder="IT / Sales" class="input input-bordered w-full bg-base-200/50 border-base-content/5 focus:border-primary/30 transition-all" required />
            </div>
            <div class="space-y-2">
              <label class="text-[10px] font-black uppercase tracking-widest opacity-40 ml-1">Phone</label>
              <input v-model="form.phone" type="text" placeholder="08x-xxxxxxx" class="input input-bordered w-full bg-base-200/50 border-base-content/5 focus:border-primary/30 transition-all" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="space-y-2">
              <label class="text-[10px] font-black uppercase tracking-widest opacity-40 ml-1">Password</label>
              <input v-model="form.password" type="password" placeholder="••••••••" class="input input-bordered w-full bg-base-200/50 border-base-content/5 focus:border-primary/30 transition-all" required />
            </div>
            <div class="space-y-2">
              <label class="text-[10px] font-black uppercase tracking-widest opacity-40 ml-1">Confirm Password</label>
              <input v-model="password_confirm" type="password" placeholder="••••••••" class="input input-bordered w-full bg-base-200/50 border-base-content/5 focus:border-primary/30 transition-all" required />
            </div>
          </div>

          <div v-if="auth.error || validationError" class="alert alert-error text-xs py-3 shadow-lg shadow-error/10">
            <span class="font-bold uppercase tracking-tight">{{ auth.error || validationError }}</span>
          </div>

          <button type="submit" class="btn btn-primary btn-block h-14 text-sm font-black uppercase tracking-[0.2em] shadow-xl shadow-primary/25 group overflow-hidden" :disabled="auth.loading">
            <span v-if="!auth.loading" class="group-hover:scale-110 transition-transform">Create Secure Account</span>
            <span v-else class="loading loading-spinner"></span>
          </button>
        </form>

        <div class="text-center mt-6 text-[10px] font-bold uppercase tracking-widest opacity-30">
          Already have an account? 
          <router-link to="/login" class="text-primary hover:underline">Sign In</router-link>
        </div>
      </div>

      <div v-else class="text-center py-8 animate-fade-in">
        <div class="w-20 h-20 bg-success/20 text-success rounded-full flex items-center justify-center text-4xl mx-auto mb-6 shadow-lg shadow-success/20">
          ✓
        </div>
        <h2 class="text-3xl font-bold bg-gradient-to-r from-success to-primary bg-clip-text text-transparent mb-4">Registration Sent!</h2>
        <p class="text-base-content/60 max-w-sm mx-auto">Your account is pending approval from Admin. We will notify you once it's ready.</p>
        <button @click="router.push('/login')" class="btn btn-primary w-full mt-10">
          Back to Login
          </button>
      </div>
    </div>
  </div>
</template>
