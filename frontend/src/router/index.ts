import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/auth',
      component: () => import('../layouts/AuthLayout.vue'),
      children: [
        {
          path: 'login',
          name: 'Login',
          component: () => import('../views/LoginPage.vue'),
          meta: { guestOnly: true },
        },
        {
          path: 'register',
          name: 'Register',
          component: () => import('../views/RegisterPage.vue'),
          meta: { guestOnly: true },
        },
      ]
    },
    {
      path: '/login',
      redirect: '/auth/login'
    },
    {
      path: '/register',
      redirect: '/auth/register'
    },
    {
      path: '/rooms',
      name: 'RoomListing',
      component: () => import('../views/RoomListing.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/rooms/:id',
      name: 'RoomDetail',
      component: () => import('../views/RoomDetail.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/rooms/:id/book',
      name: 'Booking',
      component: () => import('../views/BookingPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../views/Dashboard.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/calendar',
      name: 'Calendar',
      component: () => import('../views/CalendarPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/profile',
      name: 'Profile',
      component: () => import('../views/ProfilePage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/admin/approvals/dashboard',
      name: 'ApproverDashboard',
      component: () => import('../views/admin/ApproverDashboard.vue'),
      meta: { requiresAuth: true, requiresApprover: true },
    },
    {
      path: '/admin/approvals',
      name: 'PendingApprovals',
      component: () => import('../views/admin/PendingApprovals.vue'),
      meta: { requiresAuth: true, requiresApprover: true },
    },
    {
      path: '/admin/approvals/history',
      name: 'ApprovalHistory',
      component: () => import('../views/admin/ApprovalHistory.vue'),
      meta: { requiresAuth: true, requiresApprover: true },
    },
    {
      path: '/admin/audit-logs',
      name: 'AuditLogs',
      component: () => import('../views/admin/AuditLogs.vue'),
      meta: { requiresAuth: true, adminOnly: true },
    },
    {
      path: '/admin/settings',
      name: 'SystemSettings',
      component: () => import('../views/admin/SystemSettings.vue'),
      meta: { requiresAuth: true, adminOnly: true },
    },
    {
      path: '/admin/users',
      name: 'UserManagement',
      component: () => import('../views/admin/UserManagement.vue'),
      meta: { requiresAuth: true, adminOnly: true },
    },
    {
      path: '/admin/bookings',
      name: 'AdminBookings',
      component: () => import('../views/admin/AllBookings.vue'),
      meta: { requiresAuth: true, adminOnly: true },
    },
    {
      path: '/admin/dashboard',
      name: 'AdminDashboard',
      component: () => import('../views/admin/AdminDashboard.vue'),
      meta: { requiresAuth: true, adminOnly: true },
    },
    {
      path: '/admin/rooms',
      name: 'AdminRooms',
      component: () => import('../views/admin/RoomManagement.vue'),
      meta: { requiresAuth: true, adminOnly: true },
    },
  ],
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return '/login';
  }
  
  if (to.meta.adminOnly && !auth.isAdmin) {
    return '/dashboard';
  }

  if (to.meta.requiresApprover && !auth.isApprover) {
    return '/dashboard';
  }
  
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return '/dashboard';
  }
  
  return true;
});

export default router;
