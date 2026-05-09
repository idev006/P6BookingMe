import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  status: string;
  avatar_path?: string;
  created_at?: string;
  employee_code?: string;
  phone?: string;
}

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const token = ref<string | null>(localStorage.getItem('token'));
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const isAuthenticated = computed(() => !!token.value);
  const isAdmin = computed(() => user.value?.role === 'admin');
  const isApprover = computed(() => user.value?.role === 'approver' || user.value?.role === 'admin');

  // Actions
  const login = async (credentials: any) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.post('/auth/login/', credentials);
      const { access_token, user: userData } = response.data.data;
      
      token.value = access_token;
      user.value = userData;
      localStorage.setItem('token', access_token);
      
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'เข้าสู่ระบบไม่สำเร็จ';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const register = async (userData: any) => {
    loading.value = true;
    error.value = null;
    try {
      await api.post('/auth/register/', userData);
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'สมัครสมาชิกไม่สำเร็จ';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetchUser = async () => {
    if (!token.value) return;
    try {
      const response = await api.get('/auth/me');
      user.value = response.data.data;
    } catch (err) {
      logout();
    }
  };

  const logout = () => {
    user.value = null;
    token.value = null;
    localStorage.removeItem('token');
  };

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    isAdmin,
    isApprover,
    login,
    register,
    fetchUser,
    logout
  };
});
