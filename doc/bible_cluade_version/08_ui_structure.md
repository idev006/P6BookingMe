# 08 — UI Structure

---

## 1. Layout System

ระบบมี 3 Layout แยกกันตาม context:

```
┌─────────────────────────────────────────────────────┐
│                   AuthLayout                        │
│   ใช้สำหรับ: /login, /register                     │
│   ─────────────────────────────────────────────     │
│   กลางหน้าจอ, ไม่มี navbar, มี logo โปรเจกต์        │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                   AppLayout                         │
│   ใช้สำหรับ: /dashboard, /rooms, /bookings, ...    │
│   ─────────────────────────────────────────────     │
│  ┌─────────────────────────────────────────────┐   │
│  │  Navbar (top)                               │   │
│  │  logo | menu links | notification | avatar  │   │
│  └─────────────────────────────────────────────┘   │
│  ┌──────────┐  ┌──────────────────────────────┐    │
│  │ Sidebar  │  │     <router-view />           │    │
│  │ (left)   │  │     Page Content              │    │
│  │          │  │                               │    │
│  └──────────┘  └──────────────────────────────┘    │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                  AdminLayout                        │
│   ใช้สำหรับ: /admin/*                              │
│   ─────────────────────────────────────────────     │
│  ┌─────────────────────────────────────────────┐   │
│  │  AdminNavbar (top) — แสดง "Admin Panel"     │   │
│  └─────────────────────────────────────────────┘   │
│  ┌──────────────┐  ┌────────────────────────────┐  │
│  │ AdminSidebar │  │   <router-view />           │  │
│  │ - Dashboard  │  │   Admin Page Content        │  │
│  │ - Rooms      │  │                             │  │
│  │ - Users      │  │                             │  │
│  │ - Bookings   │  │                             │  │
│  │ - Settings   │  │                             │  │
│  │ - Audit Log  │  │                             │  │
│  └──────────────┘  └────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 2. Route Structure

```typescript
// router/index.ts

const routes = [

  // ── Public (ไม่ต้อง login) ──────────────────────────────
  {
    path: '/login',
    component: AuthLayout,
    children: [
      { path: '', name: 'login', component: LoginPage },
    ]
  },
  {
    path: '/register',
    component: AuthLayout,
    children: [
      { path: '', name: 'register', component: RegisterPage },
    ]
  },

  // ── Member / Approver (ต้อง login + active) ────────────
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '',        redirect: '/dashboard' },
      { path: 'dashboard',  name: 'dashboard',   component: DashboardPage },
      { path: 'rooms',      name: 'rooms',        component: RoomsPage },
      { path: 'rooms/:id',  name: 'room-detail',  component: RoomDetailPage },
      { path: 'bookings',   name: 'bookings',     component: BookingPage },
      { path: 'my-bookings',name: 'my-bookings',  component: MyBookingsPage },
      { path: 'my-bookings/:id', name: 'booking-detail', component: BookingDetailPage },
      { path: 'notifications',   name: 'notifications',  component: NotificationsPage },
      { path: 'profile',         name: 'profile',        component: ProfilePage },
      // Approver only
      {
        path: 'approvals',
        name: 'approvals',
        component: PendingApprovalsPage,
        meta: { requiresRole: ['approver', 'admin'] }
      },
    ]
  },

  // ── Admin ────────────────────────────────────────────────
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true, requiresRole: ['admin'] },
    children: [
      { path: '',          redirect: '/admin/dashboard' },
      { path: 'dashboard', name: 'admin-dashboard', component: AdminDashboardPage },
      { path: 'rooms',     name: 'admin-rooms',     component: AdminRoomsPage },
      { path: 'rooms/new', name: 'admin-room-new',  component: AdminRoomFormPage },
      { path: 'rooms/:id/edit', name: 'admin-room-edit', component: AdminRoomFormPage },
      { path: 'users',     name: 'admin-users',     component: AdminUsersPage },
      { path: 'bookings',  name: 'admin-bookings',  component: AdminBookingsPage },
      { path: 'settings',  name: 'admin-settings',  component: AdminSettingsPage },
      { path: 'audit-logs',name: 'admin-audit',     component: AdminAuditPage },
    ]
  },

  // ── Fallback ─────────────────────────────────────────────
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundPage },
]
```

### Navigation Guards

```typescript
// router/guards.ts

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // 1. route ต้อง login?
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // 2. route ต้องการ role เฉพาะ?
  if (to.meta.requiresRole) {
    const allowed = to.meta.requiresRole as string[]
    if (!allowed.includes(auth.user.role)) {
      return { name: 'dashboard' }  // redirect กลับ
    }
  }

  // 3. ถ้า login อยู่แล้วไปหน้า login/register → redirect dashboard
  if ((to.name === 'login' || to.name === 'register') && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
})
```

---

## 3. Page Map

### 3.1 Auth Pages

```
/login                          /register
┌──────────────────────────┐   ┌──────────────────────────┐
│  [Logo P6BookingMe]      │   │  [Logo P6BookingMe]      │
│                          │   │                          │
│  ┌────────────────────┐  │   │  ┌────────────────────┐  │
│  │  Email             │  │   │  │  Full Name         │  │
│  └────────────────────┘  │   │  └────────────────────┘  │
│  ┌────────────────────┐  │   │  ┌────────────────────┐  │
│  │  Password          │  │   │  │  Employee Code     │  │
│  └────────────────────┘  │   │  └────────────────────┘  │
│                          │   │  ┌────────────────────┐  │
│  [  เข้าสู่ระบบ  ]       │   │  │  Department        │  │
│                          │   │  └────────────────────┘  │
│  ยังไม่มีบัญชี? สมัคร   │   │  ┌────────────────────┐  │
└──────────────────────────┘   │  │  Email             │  │
                               │  └────────────────────┘  │
                               │  ┌────────────────────┐  │
                               │  │  Password          │  │
                               │  └────────────────────┘  │
                               │  ┌────────────────────┐  │
                               │  │  Phone (optional)  │  │
                               │  └────────────────────┘  │
                               │  [  สมัครสมาชิก  ]       │
                               └──────────────────────────┘
```

---

### 3.2 Member Pages

#### `/dashboard` — หน้าหลัก

```
┌─ Navbar ──────────────────────────────────────────────────┐
│  P6BookingMe  │ ห้องประชุม │ การจอง │  🔔 2  │ [Avatar] │
└───────────────────────────────────────────────────────────┘
┌─ Sidebar ─┐  ┌─ Content ─────────────────────────────────┐
│ Dashboard │  │  สวัสดี, สมชาย                            │
│ ห้องประชุม│  │                                           │
│ จองห้อง  │  │  ┌──────────────┐  ┌──────────────────┐   │
│ การจองฉัน │  │  │ การจองวันนี้ │  │ รอการอนุมัติ     │   │
│ การแจ้งเตือน│  │ │     2       │  │       1          │   │
│ โปรไฟล์   │  │  └──────────────┘  └──────────────────┘   │
└───────────┘  │                                           │
               │  ┌─ การจองล่าสุดของฉัน ─────────────────┐│
               │  │  ห้อง A  │ พรุ่งนี้ 09:00  │ Pending ││
               │  │  ห้อง B  │ 10 พ.ค. 13:00   │ Confirmed│
               │  └──────────────────────────────────────┘│
               │                                           │
               │  ┌─ ปฏิทินสัปดาห์นี้ (mini) ───────────┐ │
               │  │  [จ] [อ] [พ] [พฤ] [ศ]              │ │
               │  │   ■   ■        ■                    │ │
               │  └──────────────────────────────────────┘│
               └───────────────────────────────────────────┘
```

---

#### `/rooms` — ค้นหาห้องประชุม

```
┌─ Content ─────────────────────────────────────────────────┐
│  ค้นหาห้องประชุม                                          │
│                                                           │
│  ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │
│  │  วันที่    │ │ เวลาเริ่ม│ │ เวลาสิ้นสุด│ │ ความจุ ≥ │  │
│  │ 2026-05-10 │ │  09:00   │ │  11:00   │ │    5      │  │
│  └────────────┘ └──────────┘ └──────────┘ └───────────┘  │
│  [ ค้นหา ]                                                │
│                                                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌────────────┐  │
│  │ 🏢 ห้อง A       │ │ 🏢 ห้อง B       │ │ 🏢 ห้อง C  │  │
│  │ [รูปภาพ]        │ │ [รูปภาพ]        │ │ [รูปภาพ]   │  │
│  │ ความจุ: 10 คน  │ │ ความจุ: 20 คน  │ │ ความจุ: 6  │  │
│  │ อาคาร 1 ชั้น 3 │ │ อาคาร 2 ชั้น 5 │ │ อาคาร 1    │  │
│  │ 📽 🖊 📺        │ │ 📽 🖊 🎤        │ │ 🖊          │  │
│  │ ✅ ว่าง         │ │ ✅ ว่าง         │ │ ❌ ไม่ว่าง  │  │
│  │ [ดูรายละเอียด] │ │ [ดูรายละเอียด] │ │ [ดูรายละเอียด]│
│  └─────────────────┘ └─────────────────┘ └────────────┘  │
└───────────────────────────────────────────────────────────┘
```

---

#### `/rooms/:id` — รายละเอียดห้อง

```
┌─ Content ─────────────────────────────────────────────────┐
│  ← กลับ                                                   │
│                                                           │
│  ┌─── รูปภาพ ─────────────────────────────────────────┐  │
│  │          [รูปหลักห้องประชุม]                       │  │
│  │  [thumb1] [thumb2] [thumb3]                        │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ห้องประชุม A                          ความจุ: 10 คน     │
│  📍 อาคาร 1 ชั้น 3                                        │
│  อุปกรณ์: 📽 Projector  🖊 Whiteboard  📺 TV              │
│                                                           │
│  ┌─── ปฏิทินการจอง ──────────────────────────────────┐  │
│  │  [ < พ.ค. 2026 > ]                                │  │
│  │  จ    อ    พ    พฤ   ศ                             │  │
│  │  4    5    6    7    8                              │  │
│  │  [09:00-11:00 Confirmed] [13:00-14:00 Pending]     │  │
│  │  11   12   13   14   15                             │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│                           [ จองห้องนี้ ]                 │
└───────────────────────────────────────────────────────────┘
```

---

#### `/bookings` — หน้าจองห้อง (Booking Form)

```
┌─ Content ─────────────────────────────────────────────────┐
│  จองห้องประชุม                                            │
│                                                           │
│  ── ขั้นตอนที่ 1: เลือกห้องและเวลา ──                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │ ห้องประชุม: [ห้อง A ▼]                            │  │
│  │ วันที่:     [2026-05-10]                           │  │
│  │ เวลาเริ่ม:  [09:00 ▼]  เวลาสิ้นสุด: [11:00 ▼]    │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ── ขั้นตอนที่ 2: รายละเอียดการประชุม ──                 │
│  ┌────────────────────────────────────────────────────┐  │
│  │ หัวข้อ: [______________________________________]   │  │
│  │ รายละเอียด: [___________________________________]  │  │
│  │ จำนวนผู้เข้าร่วม: [8]                             │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ── สรุปการจอง ──                                         │
│  ┌────────────────────────────────────────────────────┐  │
│  │  ห้อง: ห้องประชุม A (ความจุ 10 คน)               │  │
│  │  วันที่: 10 พ.ค. 2569  09:00 – 11:00 (2 ชั่วโมง) │  │
│  │  หัวข้อ: ประชุมทีม Q2                             │  │
│  │  ⚠️ การจองต้องรอการอนุมัติจาก Approver            │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  [ยกเลิก]                          [ยืนยันการจอง]       │
└───────────────────────────────────────────────────────────┘
```

---

#### `/my-bookings` — รายการจองของฉัน

```
┌─ Content ─────────────────────────────────────────────────┐
│  การจองของฉัน                          [ + จองห้องใหม่ ] │
│                                                           │
│  [ทั้งหมด] [รออนุมัติ] [ยืนยันแล้ว] [ปฏิเสธ] [ยกเลิก]   │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  ห้อง A │ 10 พ.ค. 09:00-11:00 │ ●PENDING          │  │
│  │  ประชุมทีม Q2                   │ [ดูรายละเอียด]   │  │
│  ├────────────────────────────────────────────────────┤  │
│  │  ห้อง B │ 8 พ.ค. 13:00-14:00  │ ●CONFIRMED        │  │
│  │  1-on-1 Meeting                 │ [ดูรายละเอียด]   │  │
│  ├────────────────────────────────────────────────────┤  │
│  │  ห้อง A │ 5 พ.ค. 09:00-10:00  │ ●REJECTED         │  │
│  │  Sprint Planning                │ [ดูรายละเอียด]   │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  [< 1 2 3 >]                                             │
└───────────────────────────────────────────────────────────┘
```

**Status Badge Colors (DaisyUI):**
| Status | DaisyUI class | สี |
|---|---|---|
| PENDING | `badge-warning` | เหลือง |
| CONFIRMED | `badge-success` | เขียว |
| REJECTED | `badge-error` | แดง |
| CANCELLED | `badge-ghost` | เทา |

---

#### `/approvals` — รายการรออนุมัติ (Approver)

```
┌─ Content ─────────────────────────────────────────────────┐
│  รายการรออนุมัติ                          3 รายการ        │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  สมชาย ใจดี (IT)                                  │  │
│  │  ห้อง A │ 10 พ.ค. 09:00-11:00                     │  │
│  │  หัวข้อ: ประชุมทีม Q2 │ 8 คน                      │  │
│  │  จองเมื่อ: 7 พ.ค. 08:30                           │  │
│  │                    [✓ อนุมัติ]  [✗ ปฏิเสธ]        │  │
│  ├────────────────────────────────────────────────────┤  │
│  │  วิภา รักงาน (HR)                                 │  │
│  │  ห้อง B │ 11 พ.ค. 13:00-15:00                     │  │
│  │  หัวข้อ: สัมภาษณ์งาน │ 3 คน                      │  │
│  │                    [✓ อนุมัติ]  [✗ ปฏิเสธ]        │  │
│  └────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────┘

Modal เมื่อกด "ปฏิเสธ":
┌─────────────────────────────────────┐
│  ปฏิเสธการจอง                       │
│  ─────────────────────────────────  │
│  กรุณาระบุเหตุผล *                  │
│  ┌─────────────────────────────┐    │
│  │ ห้องติดซ่อมบำรุงช่วงนั้น   │    │
│  └─────────────────────────────┘    │
│                [ยกเลิก] [ยืนยัน]   │
└─────────────────────────────────────┘
```

---

### 3.3 Admin Pages

#### `/admin/dashboard`

```
┌─ AdminNavbar ─────────────────────────────────────────────┐
│  Admin Panel │ P6BookingMe                    [Avatar]   │
└───────────────────────────────────────────────────────────┘
┌─ AdminSidebar ──┐ ┌─ Content ─────────────────────────────┐
│ 📊 Dashboard    │ │  Dashboard                            │
│ 🏢 ห้องประชุม  │ │                                       │
│ 👥 สมาชิก      │ │  ┌──────────┐┌──────────┐┌──────────┐ │
│ 📋 การจอง      │ │  │การจองวันนี้││รออนุมัติ ││รอ Approve│ │
│ ⚙️ ตั้งค่า     │ │  │    12    ││    3     ││สมาชิก: 2 │ │
│ 📜 Audit Log   │ │  └──────────┘└──────────┘└──────────┘ │
└─────────────────┘ │                                       │
                    │  ┌─ อัตราการใช้ห้อง (สัปดาห์นี้) ──┐ │
                    │  │  ห้อง A  [████████░░] 80%       │ │
                    │  │  ห้อง B  [█████░░░░░] 50%       │ │
                    │  │  ห้อง C  [███░░░░░░░] 30%       │ │
                    │  └──────────────────────────────────┘ │
                    │                                       │
                    │  ┌─ การจองรายวัน (7 วัน) ───────────┐ │
                    │  │  [กราฟแท่ง]                      │ │
                    │  └──────────────────────────────────┘ │
                    └───────────────────────────────────────┘
```

---

#### `/admin/users` — จัดการสมาชิก

```
┌─ Content ──────────────────────────────────────────────────┐
│  จัดการสมาชิก                                              │
│                                                            │
│  [ทั้งหมด] [รออนุมัติ 2] [Active] [Suspended]             │
│                                                            │
│  ┌─────────┐  [ค้นหาชื่อ/email/รหัสพนักงาน...]            │
│                                                            │
│  ┌──────┬──────────────┬────────┬──────────┬───────────┐  │
│  │ ชื่อ │ หน่วยงาน   │ Role   │ Status   │ Actions   │  │
│  ├──────┼──────────────┼────────┼──────────┼───────────┤  │
│  │สมชาย│ IT           │member  │●active   │[เปลี่ยน role]│
│  ├──────┼──────────────┼────────┼──────────┼───────────┤  │
│  │วิภา │ HR           │approver│●active   │[ถอด role] │  │
│  ├──────┼──────────────┼────────┼──────────┼───────────┤  │
│  │ก้อง │ Finance      │member  │●pending  │[✓][✗]     │  │
│  └──────┴──────────────┴────────┴──────────┴───────────┘  │
└────────────────────────────────────────────────────────────┘
```

---

#### `/admin/rooms` — จัดการห้องประชุม

```
┌─ Content ──────────────────────────────────────────────────┐
│  จัดการห้องประชุม                      [+ เพิ่มห้องใหม่]  │
│                                                            │
│  ┌──────────────┬─────┬──────────────┬──────┬──────────┐  │
│  │ ชื่อห้อง    │ จุ  │ สถานที่      │Status│ Actions  │  │
│  ├──────────────┼─────┼──────────────┼──────┼──────────┤  │
│  │ ห้อง A      │ 10  │ อาคาร 1 ชั้น3│●active│[แก้ไข][ปิด]│
│  ├──────────────┼─────┼──────────────┼──────┼──────────┤  │
│  │ ห้อง B      │ 20  │ อาคาร 2 ชั้น5│●active│[แก้ไข][ปิด]│
│  ├──────────────┼─────┼──────────────┼──────┼──────────┤  │
│  │ ห้อง C      │  6  │ อาคาร 1 ชั้น2│●inactive│[แก้ไข][เปิด]│
│  └──────────────┴─────┴──────────────┴──────┴──────────┘  │
└────────────────────────────────────────────────────────────┘
```

---

#### `/admin/settings` — ตั้งค่าระบบ

```
┌─ Content ──────────────────────────────────────────────────┐
│  ตั้งค่าระบบ                                               │
│                                                            │
│  ┌─ กฎการจอง ─────────────────────────────────────────┐   │
│  │                                                    │   │
│  │  จองล่วงหน้าได้สูงสุด                             │   │
│  │  ┌──────┐ วัน     (ค่าปัจจุบัน: 30 วัน)          │   │
│  │  │  30  │                                         │   │
│  │  └──────┘                                         │   │
│  │                                                    │   │
│  │  ระยะเวลาจองสูงสุดต่อครั้ง                        │   │
│  │  ┌──────┐ ชั่วโมง  (ค่าปัจจุบัน: 4 ชั่วโมง)     │   │
│  │  │   4  │                                         │   │
│  │  └──────┘                                         │   │
│  │                                                    │   │
│  │  จองได้สูงสุดต่อวันต่อคน                          │   │
│  │  ┌──────┐ ครั้ง    (ค่าปัจจุบัน: 3 ครั้ง)        │   │
│  │  │   3  │                                         │   │
│  │  └──────┘                                         │   │
│  │                                                    │   │
│  │                              [บันทึกการตั้งค่า]   │   │
│  └────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

---

## 4. Component Tree

```
src/components/
│
├── common/                         ← Pure, ใช้ซ้ำได้ทุกที่
│   ├── AppButton.vue               props: label, variant, loading, disabled
│   ├── AppInput.vue                props: modelValue, label, error, type
│   ├── AppTextarea.vue             props: modelValue, label, error, rows
│   ├── AppSelect.vue               props: modelValue, options, label, error
│   ├── AppModal.vue                props: open, title  | emit: close
│   ├── AppBadge.vue                props: status (BookingStatus | UserStatus)
│   ├── AppPagination.vue           props: total, page, perPage | emit: change
│   ├── AppAlert.vue                props: type, message
│   └── AppSpinner.vue              props: size
│
├── booking/
│   ├── BookingCard.vue             props: booking  | emit: cancel, view
│   ├── BookingStatusBadge.vue      props: status
│   ├── BookingForm.vue             props: roomId?  | emit: submitted
│   ├── BookingDetailModal.vue      props: bookingId, open | emit: close, cancel
│   ├── CancelBookingModal.vue      props: booking, open  | emit: close, confirmed
│   └── RejectBookingModal.vue      props: booking, open  | emit: close, confirmed
│
├── room/
│   ├── RoomCard.vue                props: room, showAvailability
│   ├── RoomCalendar.vue            props: roomId, date  | emit: slot-click
│   ├── RoomImageGallery.vue        props: images
│   ├── RoomEquipmentList.vue       props: equipment[]
│   └── RoomSearchFilter.vue        props: modelValue  | emit: update:modelValue
│
├── notification/
│   └── NotificationDropdown.vue   อ่าน notificationStore โดยตรง (Smart)
│
└── layout/
    ├── AppNavbar.vue               อ่าน authStore (Smart)
    ├── AppSidebar.vue              อ่าน authStore สำหรับ role-based menu
    ├── AdminNavbar.vue
    └── AdminSidebar.vue
```

---

## 5. Pinia Stores

```typescript
// stores/authStore.ts
interface AuthState {
  token: string | null          // เก็บใน memory เท่านั้น
  user: CurrentUser | null
}
// getters: isAuthenticated, isApprover, isAdmin
// actions: login(), logout(), fetchMe(), updateProfile()

// stores/bookingStore.ts
interface BookingState {
  myBookings: Booking[]
  currentBooking: Booking | null
  pendingApprovals: Booking[]   // Approver
  calendarEvents: CalendarEvent[]
  total: number
  page: number
}
// actions: createBooking(), cancelBooking(), fetchMyBookings()
//          fetchPending(), approveBooking(), rejectBooking()
//          fetchCalendar()

// stores/roomStore.ts
interface RoomState {
  rooms: Room[]
  selectedRoom: Room | null
  total: number
}
// actions: searchRooms(), fetchRoomDetail()

// stores/notificationStore.ts
interface NotificationState {
  notifications: Notification[]
  unreadCount: number
}
// actions: fetchNotifications(), markRead(), markAllRead()

// stores/adminStore.ts  (Admin only)
interface AdminState {
  users: User[]
  pendingUsers: User[]
  configs: SystemConfig[]
  dashboardStats: DashboardStats | null
  auditLogs: AuditLog[]
}
```

---

## 6. TypeScript Types (Frontend)

```typescript
// types/user.ts
export interface User {
  id: number
  email: string
  employee_code: string
  full_name: string
  department: string
  phone: string | null
  role: UserRole
  status: UserStatus
  created_at: string
}

export interface CurrentUser extends User {}

// types/room.ts
export interface Room {
  id: number
  name: string
  capacity: number
  location: string
  building: string | null
  floor: string | null
  description: string | null
  equipment: string[]
  primary_image_url: string | null
  status: RoomStatus
  is_available?: boolean
}

// types/booking.ts
export interface Booking {
  id: number
  room_id: number
  title: string
  description: string | null
  snap_room_name: string
  snap_room_capacity: number
  snap_room_location: string
  snap_user_name: string
  snap_user_department: string
  snap_user_email: string
  start_time: string
  end_time: string
  attendee_count: number
  status: BookingStatus
  cancel_reason: string | null
  created_at: string
  approval: BookingApproval | null
}

export interface BookingApproval {
  approver_name: string
  action: ApprovalAction
  reason: string | null
  actioned_at: string
}

// types/notification.ts
export interface Notification {
  id: number
  type: NotificationType
  message: string
  booking_id: number | null
  is_read: boolean
  created_at: string
}
```

---

## 7. Page — Component Dependency Map

| Page | Stores ที่ใช้ | Components หลัก |
|---|---|---|
| `LoginPage` | authStore | AppInput, AppButton |
| `RegisterPage` | authStore | AppInput, AppButton, AppSelect |
| `DashboardPage` | authStore, bookingStore | BookingCard, RoomCalendar (mini) |
| `RoomsPage` | roomStore | RoomCard, RoomSearchFilter, AppPagination |
| `RoomDetailPage` | roomStore, bookingStore | RoomImageGallery, RoomCalendar, RoomEquipmentList |
| `BookingPage` | roomStore, bookingStore | BookingForm, AppSelect, AppInput |
| `MyBookingsPage` | bookingStore | BookingCard, BookingStatusBadge, AppPagination |
| `BookingDetailPage` | bookingStore | BookingDetailModal, CancelBookingModal |
| `PendingApprovalsPage` | bookingStore | BookingCard, RejectBookingModal, AppModal |
| `NotificationsPage` | notificationStore | AppBadge |
| `ProfilePage` | authStore | AppInput, AppButton |
| `AdminDashboardPage` | adminStore | (chart components) |
| `AdminUsersPage` | adminStore | AppPagination, AppBadge, AppModal |
| `AdminRoomsPage` | adminStore, roomStore | RoomCard, AppModal |
| `AdminRoomFormPage` | adminStore | AppInput, RoomEquipmentList, AppButton |
| `AdminBookingsPage` | adminStore | BookingCard, AppPagination |
| `AdminSettingsPage` | adminStore | AppInput, AppButton |
| `AdminAuditPage` | adminStore | AppPagination |
