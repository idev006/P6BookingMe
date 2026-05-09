<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/auth';
import { useNotificationStore } from '../../stores/notification';
import ThemeSwitcher from '../ThemeSwitcher.vue';
import { 
  LayoutDashboard, 
  CalendarRange, 
  Bell, 
  User, 
  LogOut, 
  Menu, 
  CheckCircle2, 
  AlertCircle, 
  ClipboardCheck,
  ShieldCheck,
  Settings,
  History,
  Users
} from 'lucide-vue-next';
import { formatDateTime } from '../../utils/format';

const auth = useAuthStore();
const notifStore = useNotificationStore();
const router = useRouter();
const route = useRoute();

const isActive = (path: string) => {
  if (path === '/') return route.path === '/';
  return route.path.startsWith(path);
};

const handleLogout = () => {
  auth.logout();
  router.push('/login');
};

onMounted(() => {
  if (auth.isAuthenticated) {
    notifStore.fetchNotifications();
  }
});
</script>

<template>
  <div class="navbar bg-base-100/80 backdrop-blur-md sticky top-0 z-30 border-b border-base-content/5 px-4 md:px-8">
    <div class="navbar-start">
      <div class="dropdown">
        <div tabindex="0" role="button" class="btn btn-ghost lg:hidden">
          <Menu :size="20" />
        </div>
        <ul tabindex="0" class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-200 rounded-box w-52 border border-base-content/10">
          <li><router-link to="/dashboard"><LayoutDashboard :size="16" /> Dashboard</router-link></li>
          <li><router-link to="/rooms"><CalendarRange :size="16" /> จองห้องประชุม</router-link></li>
          
          <template v-if="auth.isApprover">
            <div class="divider my-1"></div>
            <li class="menu-title">ผู้อนุมัติ</li>
            <li><router-link to="/admin/approvals/dashboard"><LayoutDashboard :size="16" /> Dashboard ผู้อนุมัติ</router-link></li>
            <li><router-link to="/admin/approvals"><ClipboardCheck :size="16" /> รายการรออนุมัติ</router-link></li>
            <li><router-link to="/admin/approvals/history"><History :size="16" /> ประวัติการอนุมัติ</router-link></li>
          </template>

          <template v-if="auth.isAdmin">
            <div class="divider my-1"></div>
            <li class="menu-title">Admin</li>
            <li><router-link to="/admin/dashboard"><LayoutDashboard :size="16" /> Dashboard ระบบ</router-link></li>
            <li><router-link to="/admin/users"><Users :size="16" /> จัดการสมาชิก</router-link></li>
            <li><router-link to="/admin/bookings"><ClipboardCheck :size="16" /> จัดการการจองทั้งหมด</router-link></li>
            <li><router-link to="/admin/rooms"><ShieldCheck :size="16" /> จัดการห้อง</router-link></li>
            <li><router-link to="/admin/audit-logs"><History :size="16" /> Audit Logs</router-link></li>
            <li><router-link to="/admin/settings"><Settings :size="16" /> ตั้งค่าระบบ</router-link></li>
          </template>
        </ul>
      </div>
      <router-link to="/" class="flex items-center gap-2 group">
        <div class="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white font-bold text-xl group-hover:scale-110 transition-transform">P</div>
        <span class="text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent hidden sm:inline-block">P6BookingMe</span>
      </router-link>
    </div>

    <div class="navbar-center hidden lg:flex">
      <ul class="menu menu-horizontal px-1 gap-1">
        <li><router-link to="/dashboard" class="px-4 py-2 rounded-xl transition-all hover:bg-base-200" exact-active-class="active-link">Dashboard</router-link></li>
        <li><router-link to="/rooms" class="px-4 py-2 rounded-xl transition-all hover:bg-base-200" exact-active-class="active-link">จองห้องประชุม</router-link></li>
        <li><router-link to="/calendar" class="px-4 py-2 rounded-xl transition-all hover:bg-base-200" exact-active-class="active-link">ปฏิทิน</router-link></li>
        
        <li v-if="auth.isApprover" class="dropdown">
          <div tabindex="0" role="button" class="px-4 py-2 rounded-xl flex items-center gap-1 transition-all hover:bg-base-200" :style="isActive('/admin/approvals') ? { color: 'oklch(var(--p))', fontWeight: 'bold' } : {}">
            <ClipboardCheck :size="18" />
            เมนูผู้อนุมัติ
          </div>
          <ul tabindex="0" class="dropdown-content menu p-2 shadow-2xl bg-base-100 rounded-box w-52 border border-base-content/10 z-[110] mt-2">
            <li><router-link to="/admin/approvals/dashboard" exact-active-class="bg-primary/10 text-primary font-bold">Dashboard ผู้อนุมัติ</router-link></li>
            <li><router-link to="/admin/approvals" exact-active-class="bg-primary/10 text-primary font-bold">รายการรออนุมัติ</router-link></li>
            <li><router-link to="/admin/approvals/history" exact-active-class="bg-primary/10 text-primary font-bold">ประวัติการอนุมัติ</router-link></li>
          </ul>
        </li>

        <li v-if="auth.isAdmin" class="dropdown">
          <div tabindex="0" role="button" class="px-4 py-2 rounded-xl flex items-center gap-1 transition-all hover:bg-base-200" :style="isActive('/admin') && !isActive('/admin/approvals') ? { color: 'oklch(var(--p))', fontWeight: 'bold' } : {}">
            <ShieldCheck :size="18" />
            แผงควบคุม Admin
          </div>
          <ul tabindex="0" class="dropdown-content menu p-2 shadow-2xl bg-base-100 rounded-box w-52 border border-base-content/10 z-[110] mt-2">
            <li><router-link to="/admin/dashboard" exact-active-class="bg-primary/10 text-primary font-bold">Dashboard ระบบ</router-link></li>
            <li><router-link to="/admin/users" exact-active-class="bg-primary/10 text-primary font-bold">จัดการสมาชิก</router-link></li>
            <li><router-link to="/admin/bookings" exact-active-class="bg-primary/10 text-primary font-bold">จัดการการจองทั้งหมด</router-link></li>
            <li><router-link to="/admin/rooms" exact-active-class="bg-primary/10 text-primary font-bold">จัดการห้องประชุม</router-link></li>
            <li><router-link to="/admin/audit-logs" exact-active-class="bg-primary/10 text-primary font-bold">Audit Logs</router-link></li>
            <li><router-link to="/admin/settings" exact-active-class="bg-primary/10 text-primary font-bold">ตั้งค่าระบบ</router-link></li>
          </ul>
        </li>
      </ul>
    </div>

    <div class="navbar-end gap-2">
      <div class="hidden md:block">
        <ThemeSwitcher />
      </div>

      <!-- Notifications Dropdown -->
      <div v-if="auth.isAuthenticated" class="dropdown dropdown-end">
        <div tabindex="0" role="button" class="btn btn-ghost btn-circle">
          <div class="indicator">
            <Bell :size="20" />
            <span v-if="notifStore.unreadCount > 0" class="badge badge-xs badge-primary indicator-item"></span>
          </div>
        </div>
        <div tabindex="0" class="mt-3 z-[100] card card-compact dropdown-content w-80 bg-base-100 shadow-2xl border border-base-content/10">
          <div class="card-body">
            <div class="flex justify-between items-center mb-2">
              <h3 class="font-bold text-lg">การแจ้งเตือน</h3>
              <button @click="notifStore.markAllRead" class="btn btn-ghost btn-xs text-primary">อ่านทั้งหมด</button>
            </div>
            
            <div class="flex flex-col max-h-96 overflow-y-auto gap-2">
              <div v-for="notif in notifStore.notifications" :key="notif.id" 
                class="flex gap-3 p-3 rounded-xl hover:bg-base-200 transition-colors cursor-pointer border-l-4"
                :class="notif.is_read ? 'border-transparent' : 'border-primary bg-primary/5'">
                <div class="mt-1">
                  <CheckCircle2 v-if="notif.type.includes('confirmed')" :size="16" class="text-success" />
                  <AlertCircle v-else :size="16" class="text-error" />
                </div>
                <div class="flex-grow">
                  <p class="text-sm leading-tight text-base-content">{{ notif.message }}</p>
                  <span class="text-[10px] opacity-50 mt-1 block">{{ formatDateTime(notif.created_at) }}</span>
                </div>
              </div>
              
              <div v-if="notifStore.notifications.length === 0" class="py-10 text-center text-base-content/30 italic">
                ไม่มีการแจ้งเตือนในขณะนี้
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="auth.isAuthenticated" class="dropdown dropdown-end">
        <div tabindex="0" role="button" class="btn btn-ghost btn-circle avatar border border-base-content/10">
          <div class="w-10 rounded-full bg-base-200 flex items-center justify-center">
            <User :size="20" class="text-base-content/50" />
          </div>
        </div>
        <ul tabindex="0" class="mt-3 z-[100] p-2 shadow menu menu-sm dropdown-content bg-base-100 rounded-box w-52 border border-base-content/10">
          <li class="px-4 py-2 font-bold text-primary">{{ auth.user?.full_name }}</li>
          <div class="divider my-0"></div>
          <li><router-link to="/profile"><User :size="16" /> โปรไฟล์</router-link></li>
          <div class="divider my-0"></div>
          <li><a @click="handleLogout" class="text-error"><LogOut :size="16" /> ออกจากระบบ</a></li>
        </ul>
      </div>
      <router-link v-else to="/login" class="btn btn-primary btn-sm px-6">Login</router-link>
    </div>
  </div>
</template>

<style scoped>
.active-link {
  color: oklch(var(--p));
  font-weight: 700;
  background-color: oklch(var(--p) / 0.05);
  border-radius: 0.75rem;
  position: relative;
}

.active-link::after {
  content: '';
  position: absolute;
  bottom: -0.25rem;
  left: 50%;
  transform: translateX(-50%);
  width: 0.375rem;
  height: 0.375rem;
  background-color: oklch(var(--p));
  border-radius: 9999px;
  box-shadow: 0 0 8px oklch(var(--p) / 0.5);
}

.menu li a {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}
</style>
