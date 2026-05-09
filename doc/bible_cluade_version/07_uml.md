# 07 — UML Diagrams

---

## 1. State Machine Diagrams

### 1.1 User Account Status

```
                        ┌─────────────┐
                        │   (start)   │
                        └──────┬──────┘
                               │ POST /auth/register
                        ┌──────▼──────┐
                        │   PENDING   │◄─────────────────────────────┐
                        └──────┬──────┘                              │
               Admin           │              Admin                  │
              Approve          │              Reject                 │
        ┌──────────────────────┤                                     │
        │                      │ reject                              │
 ┌──────▼──────┐        ┌───────▼──────┐                            │
 │   ACTIVE    │        │   REJECTED   │ (terminal — ไม่สามารถใช้งาน│
 └──────┬──────┘        └──────────────┘  ได้อีก)                   │
        │                                                             │
        │ Admin Suspend                                               │
 ┌──────▼──────┐                                                     │
 │  SUSPENDED  │                                                     │
 └──────┬──────┘                                                     │
        │ Admin Reactivate                                            │
        └─────────────────────────────────────────────────────────────┘

ข้อกำหนด:
- PENDING   → ไม่สามารถ Login ได้
- REJECTED  → ไม่สามารถ Login ได้ (terminal state)
- SUSPENDED → ไม่สามารถ Login และสร้าง Booking ใหม่ได้
- ACTIVE    → ใช้งานได้ปกติ
```

---

### 1.2 Booking Status

```
                        ┌─────────────┐
                        │   (start)   │
                        └──────┬──────┘
                               │ POST /bookings (Member)
                        ┌──────▼──────┐
                  ┌─────┤   PENDING   ├─────┐
                  │     └──────┬──────┘     │
                  │            │            │
         Member/Admin          │       Approver
           Cancel              │       Reject
                  │     Approver│Approve     │
                  │      ┌──────▼──────┐     │
                  │      │  CONFIRMED  │     │
                  │      └──────┬──────┘     │
                  │             │            │
                  │    Member/Admin Cancel   │
                  │             │            │
           ┌──────▼─────────────▼──────┐    │
           │        CANCELLED          │    │
           └───────────────────────────┘    │
                                     ┌──────▼──────┐
                                     │  REJECTED   │
                                     └─────────────┘

ข้อกำหนด:
- PENDING   → Member ยกเลิกเองได้, Admin ยกเลิกได้, Approver อนุมัติ/ปฏิเสธได้
- CONFIRMED → Member ยกเลิกได้ (ต้องระบุเหตุผล), Admin ยกเลิกได้
- REJECTED  → terminal state (ไม่มีการเปลี่ยนแปลงอีก)
- CANCELLED → terminal state (ไม่มีการเปลี่ยนแปลงอีก)
```

---

## 2. Sequence Diagrams

### 2.1 Member Registration & Admin Approval

```
Member          Frontend         Backend API      Database       Admin
  │                │                 │               │             │
  │ กรอกฟอร์มสมัคร │                 │               │             │
  │──────────────►│                 │               │             │
  │               │ POST /auth/register              │             │
  │               │────────────────►│               │             │
  │               │                 │ validate input │             │
  │               │                 │───────────────►│             │
  │               │                 │ INSERT user    │             │
  │               │                 │ status=pending │             │
  │               │                 │◄───────────────│             │
  │               │                 │ INSERT audit_log             │
  │               │                 │───────────────►│             │
  │               │ 201 {status:"pending"}           │             │
  │               │◄────────────────│               │             │
  │ แสดง "รอการอนุมัติ"             │               │             │
  │◄──────────────│                 │               │             │
  │               │                 │               │             │
  │               │                 │          Admin เปิด pending list
  │               │                 │               │◄────────────│
  │               │                 │ GET /admin/users/pending     │
  │               │                 │◄──────────────────────────── │
  │               │                 │ SELECT users WHERE           │
  │               │                 │ status='pending'             │
  │               │                 │───────────────►│             │
  │               │                 │◄───────────────│             │
  │               │                 │──────────────────────────────►
  │               │                 │               │             │ ดูรายการ
  │               │                 │               │             │
  │               │                 │          Admin กด Approve    │
  │               │                 │ POST /admin/users/{id}/approve
  │               │                 │◄──────────────────────────── │
  │               │                 │ UPDATE user status='active'  │
  │               │                 │───────────────►│             │
  │               │                 │ INSERT audit_log             │
  │               │                 │───────────────►│             │
  │               │                 │ 200 {status:"active"}        │
  │               │                 │──────────────────────────────►
  │               │                 │               │             │ สำเร็จ
```

---

### 2.2 Login Flow

```
Member          Frontend          Backend API      Database
  │                │                  │               │
  │ กรอก email+pass│                  │               │
  │───────────────►│                  │               │
  │                │ POST /auth/login │               │
  │                │─────────────────►│               │
  │                │                  │ SELECT user   │
  │                │                  │ WHERE email=? │
  │                │                  │──────────────►│
  │                │                  │◄──────────────│
  │                │                  │               │
  │                │                  ├─ user found? ─┤
  │                │                  │ verify bcrypt │
  │                │                  │ password hash │
  │                │                  │               │
  │                │                  ├─ status check─┤
  │                │                  │ pending?  → 403 ACCOUNT_PENDING
  │                │                  │ suspended?→ 403 ACCOUNT_SUSPENDED
  │                │                  │ active?   → ผ่าน
  │                │                  │               │
  │                │                  │ encode JWT    │
  │                │                  │ {user_id, role│
  │                │                  │  exp: +8h}    │
  │                │                  │               │
  │                │ 200 {access_token, user}         │
  │                │◄─────────────────│               │
  │                │ เก็บ token ใน    │               │
  │                │ Pinia authStore  │               │
  │                │ (memory only)    │               │
  │ redirect ตาม role               │               │
  │◄───────────────│                  │               │
```

---

### 2.3 Create Booking (Critical Path — Conflict Check)

```
Member        Frontend       Backend API    BookingService   Database
  │               │               │               │              │
  │ เลือกห้อง+เวลา│               │               │              │
  │──────────────►│               │               │              │
  │               │ POST /bookings│               │              │
  │               │──────────────►│               │              │
  │               │               │ get_current_user()           │
  │               │               │──────────────────────────────►
  │               │               │ SELECT user (check active)   │
  │               │               │◄─────────────────────────────│
  │               │               │               │              │
  │               │               │ booking_service.create()     │
  │               │               │──────────────►│              │
  │               │               │               │              │
  │               │               │               ├─ validate rules ─┤
  │               │               │               │ max_advance_days?│
  │               │               │               │ max_hours?       │
  │               │               │               │ bookings/day?    │
  │               │               │               │ attendee ≤ cap?  │
  │               │               │               │──────────────►│
  │               │               │               │◄──────────────│
  │               │               │               │              │
  │               │               │               │ BEGIN TRANSACTION
  │               │               │               │──────────────►│
  │               │               │               │              │
  │               │               │               │ SELECT * FROM bookings
  │               │               │               │ WHERE room_id=?  │
  │               │               │               │ AND status IN    │
  │               │               │               │ ('pending','confirmed')
  │               │               │               │ AND time overlap │
  │               │               │               │ FOR UPDATE ←lock│
  │               │               │               │──────────────►│
  │               │               │               │◄──────────────│
  │               │               │               │              │
  │               │               │        ┌──────▼──────┐       │
  │               │               │        │ มี conflict?│       │
  │               │               │        └──────┬──────┘       │
  │               │               │    YES ─────► │ ROLLBACK     │
  │               │               │    409 BOOKING_CONFLICT       │
  │               │               │◄──────────────│              │
  │               │ 409 error     │               │              │
  │◄──────────────│               │               │              │
  │ แสดง error msg│               │               │              │
  │               │               │               │              │
  │               │               │    NO ──────► │              │
  │               │               │               │ build snapshot│
  │               │               │               │ INSERT booking│
  │               │               │               │──────────────►│
  │               │               │               │ INSERT notification
  │               │               │               │ (to Approvers)│
  │               │               │               │──────────────►│
  │               │               │               │ INSERT audit_log
  │               │               │               │──────────────►│
  │               │               │               │ COMMIT        │
  │               │               │               │──────────────►│
  │               │               │◄──────────────│              │
  │               │ 201 {booking, status:"pending"}              │
  │◄──────────────│               │               │              │
  │ แสดง "รอการอนุมัติ"           │               │              │
```

---

### 2.4 Approver — Approve Booking

```
Approver      Frontend       Backend API    BookingService   Database    Member
  │               │               │               │              │          │
  │ เปิดหน้า      │               │               │              │          │
  │ Pending List  │               │               │              │          │
  │──────────────►│               │               │              │          │
  │               │ GET /approvals/pending         │              │          │
  │               │──────────────►│               │              │          │
  │               │               │──────────────────────────────►          │
  │               │               │ SELECT bookings WHERE        │          │
  │               │               │ status='pending'             │          │
  │               │               │◄─────────────────────────────│          │
  │               │ 200 [bookings]│               │              │          │
  │◄──────────────│               │               │              │          │
  │               │               │               │              │          │
  │ กด Approve    │               │               │              │          │
  │──────────────►│               │               │              │          │
  │               │ POST /approvals/{id}/approve  │              │          │
  │               │──────────────►│               │              │          │
  │               │               │ approval_service.approve()   │          │
  │               │               │──────────────►│              │          │
  │               │               │               │              │          │
  │               │               │               │ BEGIN TRANSACTION       │
  │               │               │               │──────────────►          │
  │               │               │               │ SELECT booking          │
  │               │               │               │ WHERE id=?              │
  │               │               │               │ FOR UPDATE   │          │
  │               │               │               │──────────────►          │
  │               │               │               │◄─────────────│          │
  │               │               │               │              │          │
  │               │               │        ┌──────▼──────┐       │          │
  │               │               │        │ still pending?      │          │
  │               │               │        └──────┬──────┘       │          │
  │               │               │    NO ──────►│ 400 error     │          │
  │               │               │◄─────────────│              │          │
  │               │               │               │              │          │
  │               │               │    YES ─────► │              │          │
  │               │               │               │ re-check conflict       │
  │               │               │               │ (อาจมีคนจองซ้อน        │
  │               │               │               │  ระหว่างรออนุมัติ)     │
  │               │               │        ┌──────▼──────┐       │          │
  │               │               │        │ conflict now?       │          │
  │               │               │        └──────┬──────┘       │          │
  │               │               │    YES ──────►│ ROLLBACK     │          │
  │               │               │    409 BOOKING_CONFLICT       │          │
  │               │               │◄──────────────│              │          │
  │               │               │               │              │          │
  │               │               │    NO ──────► │              │          │
  │               │               │               │ UPDATE booking          │
  │               │               │               │ status='confirmed'      │
  │               │               │               │──────────────►          │
  │               │               │               │ INSERT booking_approval  │
  │               │               │               │──────────────►          │
  │               │               │               │ INSERT notification      │
  │               │               │               │ type='booking_confirmed' │
  │               │               │               │ to member    │──────────►
  │               │               │               │ INSERT audit_log         │
  │               │               │               │──────────────►          │
  │               │               │               │ COMMIT        │          │
  │               │               │               │──────────────►          │
  │               │               │◄──────────────│              │          │
  │               │ 200 {action:"approved"}        │              │          │
  │◄──────────────│               │               │              │          │
  │ แสดงสำเร็จ    │               │               │              │          │
  │               │               │               │              │   รับ notification
```

---

### 2.5 Approver — Reject Booking

```
Approver      Frontend       Backend API    BookingService   Database    Member
  │               │               │               │              │          │
  │ กด Reject     │               │               │              │          │
  │ กรอกเหตุผล   │               │               │              │          │
  │──────────────►│               │               │              │          │
  │               │ POST /approvals/{id}/reject   │              │          │
  │               │ body: {reason}│               │              │          │
  │               │──────────────►│               │              │          │
  │               │               │ validate reason (required)   │          │
  │               │               │ approval_service.reject()    │          │
  │               │               │──────────────►│              │          │
  │               │               │               │ BEGIN TRANSACTION       │
  │               │               │               │ UPDATE booking          │
  │               │               │               │ status='rejected'       │
  │               │               │               │──────────────►          │
  │               │               │               │ INSERT booking_approval  │
  │               │               │               │ action='rejected'        │
  │               │               │               │ reason=...   │          │
  │               │               │               │──────────────►          │
  │               │               │               │ INSERT notification      │
  │               │               │               │ type='booking_rejected'  │
  │               │               │               │ message=reason│─────────►
  │               │               │               │ INSERT audit_log         │
  │               │               │               │──────────────►          │
  │               │               │               │ COMMIT        │          │
  │               │               │◄──────────────│              │          │
  │               │ 200 {action:"rejected"}        │              │          │
  │◄──────────────│               │               │              │   รับ notification
  │               │               │               │              │   พร้อมเหตุผล
```

---

### 2.6 Cancel Booking (Member)

```
Member        Frontend       Backend API    BookingService   Database
  │               │               │               │              │
  │ กด ยกเลิก    │               │               │              │
  │ กรอกเหตุผล   │               │               │              │
  │──────────────►│               │               │              │
  │               │ DELETE /bookings/{id}         │              │
  │               │ body: {reason}│               │              │
  │               │──────────────►│               │              │
  │               │               │ get_current_user()           │
  │               │               │──────────────────────────────►
  │               │               │◄─────────────────────────────│
  │               │               │ booking_service.cancel()     │
  │               │               │──────────────►│              │
  │               │               │               │ SELECT booking│
  │               │               │               │──────────────►│
  │               │               │               │◄──────────────│
  │               │               │        ┌──────▼──────┐       │
  │               │               │        │ owner check │       │
  │               │               │        │ booking.user│       │
  │               │               │        │ _id == me?  │       │
  │               │               │        └──────┬──────┘       │
  │               │               │    NO ──────► 403 Forbidden  │
  │               │               │               │              │
  │               │               │    YES ─────► │              │
  │               │               │        ┌──────▼──────┐       │
  │               │               │        │ status check│       │
  │               │               │        │ pending or  │       │
  │               │               │        │ confirmed?  │       │
  │               │               │        └──────┬──────┘       │
  │               │               │    NO ──────► 400 CANNOT_CANCEL
  │               │               │               │              │
  │               │               │    YES ─────► │              │
  │               │               │               │ UPDATE booking│
  │               │               │               │ status='cancelled'
  │               │               │               │ cancel_reason=?
  │               │               │               │ cancelled_by=me
  │               │               │               │──────────────►│
  │               │               │               │ INSERT audit_log
  │               │               │               │──────────────►│
  │               │               │◄──────────────│              │
  │               │ 200 {status:"cancelled"}       │              │
  │◄──────────────│               │               │              │
```

---

### 2.7 Admin Manage Room (Create)

```
Admin         Frontend       Backend API    RoomService     Database
  │               │               │               │              │
  │ กรอกข้อมูลห้อง│               │               │              │
  │──────────────►│               │               │              │
  │               │ POST /admin/rooms              │              │
  │               │──────────────►│               │              │
  │               │               │ require_admin()│              │
  │               │               │ room_service.create()        │
  │               │               │──────────────►│              │
  │               │               │               │ INSERT room  │
  │               │               │               │──────────────►│
  │               │               │               │ INSERT equipment (loop)
  │               │               │               │──────────────►│
  │               │               │               │ INSERT audit_log
  │               │               │               │──────────────►│
  │               │               │◄──────────────│              │
  │               │ 201 room object│               │              │
  │◄──────────────│               │               │              │
  │               │               │               │              │
  │ อัปโหลดรูป    │               │               │              │
  │──────────────►│               │               │              │
  │               │ POST /admin/rooms/{id}/images  │              │
  │               │ multipart/form-data            │              │
  │               │──────────────►│               │              │
  │               │               │ save file to disk            │
  │               │               │ INSERT room_images           │
  │               │               │──────────────────────────────►
  │               │ 201 image object               │              │
  │◄──────────────│               │               │              │
```

---

### 2.8 JWT Authentication Flow (Every Protected Request)

```
Client          Frontend          Backend Middleware       Database
  │                │                     │                    │
  │ ทุก request    │                     │                    │
  │                │ Header:             │                    │
  │                │ Authorization:      │                    │
  │                │ Bearer <token>      │                    │
  │                │────────────────────►│                    │
  │                │                     │ decode JWT          │
  │                │                     ├─ signature valid? ─┤
  │                │                     │ NO → 401           │
  │                │                     │                    │
  │                │                     ├─ token expired? ───┤
  │                │                     │ YES → 401          │
  │                │                     │                    │
  │                │                     │ SELECT user        │
  │                │                     │ WHERE id=user_id   │
  │                │                     │───────────────────►│
  │                │                     │◄───────────────────│
  │                │                     │                    │
  │                │                     ├─ status check ─────┤
  │                │                     │ pending/rejected/  │
  │                │                     │ suspended → 403    │
  │                │                     │                    │
  │                │                     ├─ role check ───────┤
  │                │                     │ (ถ้า endpoint      │
  │                │                     │ ต้องการ role)      │
  │                │                     │ insufficient → 403 │
  │                │                     │                    │
  │                │                     │ ✅ ผ่านทุกcheck    │
  │                │                     │ inject CurrentUser │
  │                │                     │ เข้า handler       │
  │                │                     │                    │
  │                │           proceed to endpoint handler    │
```

---

## 3. Component Interaction Diagram (Frontend)

```
┌─────────────────────────────────────────────────────────────┐
│                       Vue Router                            │
│  /login  /register  /dashboard  /bookings  /admin/*        │
│  Navigation Guards: ตรวจ authStore.isAuthenticated + role   │
└──────────────────────────┬──────────────────────────────────┘
                           │ render
          ┌────────────────┴─────────────────┐
          │                                  │
┌─────────▼──────────┐              ┌────────▼───────────┐
│   Pages (Smart)    │              │   Pages (Smart)    │
│  DashboardPage     │              │  AdminDashboard    │
│  BookingPage       │              │  RoomsPage         │
│  MyBookingsPage    │              │  UsersPage         │
│  PendingApprovals  │              │  SettingsPage      │
└────────┬───────────┘              └────────┬───────────┘
         │ read/dispatch                      │ read/dispatch
         ▼                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      Pinia Stores                           │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  authStore  │  │ bookingStore │  │    roomStore      │  │
│  │  token      │  │  bookings    │  │    rooms          │  │
│  │  user       │  │  pending     │  │    selectedRoom   │  │
│  │  isLoggedIn │  │  calendar    │  │                   │  │
│  └──────┬──────┘  └──────┬───────┘  └─────────┬─────────┘  │
└─────────┼────────────────┼──────────────────────┼───────────┘
          │ calls          │ calls                │ calls
          ▼                ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                           │
│  authService        bookingService       roomService        │
│  .login()           .create()            .search()          │
│  .register()        .cancel()            .getDetail()       │
│  .getMe()           .getMyBookings()                        │
└──────────────────────────┬──────────────────────────────────┘
                           │ axios + JWT header
                           ▼
                  ┌─────────────────┐
                  │   Axios Client  │
                  │  interceptor:   │
                  │  แนบ Bearer     │
                  │  token ทุก req  │
                  └────────┬────────┘
                           │ HTTP/REST
                           ▼
                  ┌─────────────────┐
                  │  FastAPI Backend │
                  │  localhost:8000  │
                  └─────────────────┘

Pure Components (ไม่รู้จัก Store):
┌──────────────┐  ┌───────────────┐  ┌──────────────────┐
│  RoomCard    │  │TimeSlotPicker │  │   BookingCard    │
│  props:room  │  │ props:slots   │  │  props:booking   │
│  emit:select │  │ emit:selected │  │  emit:cancel     │
└──────────────┘  └───────────────┘  └──────────────────┘
```

---

## 4. Deployment Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Developer Machine                        │
│                                                             │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │   Frontend Dev       │    │     Backend Dev          │  │
│  │   localhost:5173     │    │     localhost:8000       │  │
│  │                      │    │                          │  │
│  │  npm run dev         │    │  uvicorn app.main:app    │  │
│  │  (Vite HMR)          │◄──►│  --reload                │  │
│  │                      │CORS│                          │  │
│  └──────────────────────┘    │  ┌────────────────────┐  │  │
│                              │  │  SQLite            │  │  │
│                              │  │  data/bookingme.db │  │  │
│                              │  └────────────────────┘  │  │
│                              └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  Production (future)                        │
│                                                             │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │   Nginx              │    │   Gunicorn + Uvicorn     │  │
│  │   serve dist/        │    │   workers                │  │
│  │   proxy /api → :8000 │◄──►│   port: 8000             │  │
│  └──────────────────────┘    │                          │  │
│                              │  ┌────────────────────┐  │  │
│                              │  │  MySQL / MariaDB   │  │  │
│                              │  │  or PostgreSQL     │  │  │
│                              │  └────────────────────┘  │  │
│                              └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Summary — Diagrams Index

| Diagram | ประเภท | ความสำคัญ |
|---|---|---|
| 1.1 User Account Status | State Machine | กำหนด lifecycle ของ account |
| 1.2 Booking Status | State Machine | กำหนด lifecycle ของการจอง |
| 2.1 Register & Admin Approval | Sequence | Flow การสมัครสมาชิก |
| 2.2 Login | Sequence | JWT authentication flow |
| 2.3 Create Booking | Sequence | **Critical** — Conflict check + snapshot |
| 2.4 Approve Booking | Sequence | **Critical** — Re-check conflict ตอน approve |
| 2.5 Reject Booking | Sequence | Rejection + notification |
| 2.6 Cancel Booking | Sequence | Owner check + status check |
| 2.7 Admin Create Room | Sequence | Room + image management |
| 2.8 JWT Auth Flow | Sequence | **Critical** — DB status check ทุก request |
| 3. Component Interaction | Component | Frontend architecture |
| 4. Deployment | Deployment | Dev vs Production |
