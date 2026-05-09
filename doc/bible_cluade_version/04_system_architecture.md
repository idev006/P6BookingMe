# 04 — System Architecture

---

## 1. Architecture Overview

P6BookingMe ใช้สถาปัตยกรรมแบบ **Monolith with Strict Layering** ตามหลักการใน `00_design_philosophy.md`

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Browser                           │
│           Vue 3 + Vite (create-vue) + TypeScript                │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Pinia Store  │  Vue Router  │  Axios (HTTP Client)     │   │
│   └─────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/REST JSON
                            │ (localhost:8000 / production domain)
┌───────────────────────────▼─────────────────────────────────────┐
│                     FastAPI Application                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  API Layer (Routers)                                     │   │
│  │  /api/v1/auth  /api/v1/rooms  /api/v1/bookings          │   │
│  │  /api/v1/users  /api/v1/admin  /api/v1/notifications    │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │ validated Pydantic schemas            │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │  Service Layer (Business Logic)                          │   │
│  │  AuthService  RoomService  BookingService                │   │
│  │  UserService  NotificationService  ConfigService         │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │ domain objects                        │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │  Repository Layer (Data Access)                          │   │
│  │  UserRepo  RoomRepo  BookingRepo  AuditRepo              │   │
│  └──────────────────────┬───────────────────────────────────┘   │
│                         │ SQLAlchemy ORM                        │
│  ┌──────────────────────▼───────────────────────────────────┐   │
│  │  Database                                                │   │
│  │  SQLite (dev)  →  PostgreSQL (production-ready)          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Stack

### Frontend

| รายการ | เทคโนโลยี | เหตุผล |
|---|---|---|
| Scaffolding | `npm create vue@latest` | Official Vue scaffolding — Vite + Vue Router + Pinia พร้อมใช้ |
| Build Tool | Vite (via create-vue) | Fast HMR, native ESM — ใช้ผ่าน @tailwindcss/vite plugin |
| Framework | Vue 3 (Composition API) | Reactive, TypeScript-first |
| Language | TypeScript | Type safety, better IDE support |
| State Management | Pinia | เลือกได้ตอน create-vue init |
| HTTP Client | Axios | Interceptor support สำหรับ JWT |
| Form Validation | Zod + VeeValidate | Type-safe schema validation |
| CSS Framework | TailwindCSS v4 + @tailwindcss/vite | ไม่ต้องใช้ PostCSS config, config ผ่าน CSS |
| UI Components | DaisyUI v5 | Component library บน Tailwind v4, theme support |
| Router | Vue Router 4 | เลือกได้ตอน create-vue init, Navigation Guards สำหรับ Auth |

### Backend

| รายการ | เทคโนโลยี | เหตุผล |
|---|---|---|
| Language | Python 3.12 | Latest stable, match virtual env |
| Framework | FastAPI 0.115 | Async, auto OpenAPI docs, Pydantic native |
| ORM | SQLAlchemy 2.0 (async) | Mature, type-safe, supports async |
| Migration | Alembic | Standard migration tool สำหรับ SQLAlchemy |
| Validation | Pydantic v2 | FastAPI native, fast, type-safe |
| Auth | python-jose + passlib | JWT encode/decode + bcrypt hashing |
| Settings | pydantic-settings | `.env` driven configuration |
| ASGI Server | Uvicorn + Gunicorn | Production-ready async server |
| Testing | pytest + pytest-asyncio + httpx | Async integration testing |
| Packaging | PyInstaller | รองรับการ Build เป็น Executable แบบ Standalone (.exe) |

### Frontend Testing & Automation
| รายการ | เทคโนโลยี | เหตุผล |
|---|---|---|
| E2E Testing | Playwright with AI | ใช้ AI ช่วยเขียนและซ่อมแซม Test Script อัตโนมัติ (Self-healing locators) |

### Database

| Environment | Database | Async Driver | เหตุผล |
|---|---|---|---|
| Development | SQLite | `aiosqlite` | Zero config, portable, เริ่มต้นง่าย |
| Production (option A) | MySQL / MariaDB | `aiomysql` | นิยมในองค์กร, hosting ง่าย |
| Production (option B) | PostgreSQL | `asyncpg` | ACID เข้มแข็ง, row-level locking ดีที่สุด |

**การเปลี่ยน Database ทำได้โดยเปลี่ยนแค่ `DATABASE_URL` ใน `.env` เท่านั้น — ไม่ต้องแตะโค้ด** เพราะใช้ SQLAlchemy ORM เป็น abstraction layer

```bash
# SQLite (dev)
DATABASE_URL=sqlite+aiosqlite:///./data/bookingme.db

# MySQL / MariaDB
DATABASE_URL=mysql+aiomysql://user:pass@localhost:3306/bookingme

# PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/bookingme
```

> **ADR:** เลือกใช้ SQLAlchemy ORM เพื่อให้ switch database ได้โดยไม่แก้โค้ด
> ห้าม raw SQL ในทุก layer ยกเว้น Migration (Alembic)

---

## 3. Layer Architecture (Backend)

### 3.1 API Layer (Router)

**หน้าที่:** รับ HTTP Request → ตรวจสอบ Authentication → เรียก Service → คืน Response

**กฎเหล็ก:**
- มีได้เฉพาะ: Auth check, Schema validation, เรียก Service method
- ห้ามมี: Business logic, Database query, Calculation ใดๆ

```python
# ✅ ถูกต้อง
@router.post("/bookings", response_model=BookingResponse)
async def create_booking(
    body: BookingCreate,
    current_user: CurrentUser = Depends(get_current_active_user),
    booking_service: BookingService = Depends(),
):
    return await booking_service.create(current_user, body)

# ❌ ผิด — มี business logic ใน router
@router.post("/bookings")
async def create_booking(body: BookingCreate, db: Session = Depends()):
    conflict = db.query(Booking).filter(...).first()  # ← ห้าม
    if conflict:
        raise HTTPException(...)
```

### 3.2 Service Layer (Business Logic)

**หน้าที่:** จัดการกฎทางธุรกิจทั้งหมด เช่น Conflict Check, Rule Validation, Workflow

**กฎเหล็ก:**
- เป็นเจ้าของ Business Logic ทั้งหมด
- เรียก Repository เพื่อเข้าถึงข้อมูล
- ห้ามเรียก Database โดยตรง (ผ่าน Repository เท่านั้น)

```python
# ✅ ถูกต้อง
class BookingService:
    async def create(self, user: CurrentUser, data: BookingCreate) -> Booking:
        await self._validate_booking_rules(user, data)   # Business rules
        await self._check_conflict(data)                 # Conflict check
        snapshot = self._build_snapshot(user, data)      # Snapshot pattern
        return await self.booking_repo.create(snapshot)  # เรียก repo
```

### 3.3 Repository Layer (Data Access)

**หน้าที่:** จัดการทุก Database query ให้อยู่ที่เดียว

**กฎเหล็ก:**
- ทุก query ต้องอยู่ใน Repository method เท่านั้น
- ใช้ `selectinload()` / `joinedload()` สำหรับ relationship เสมอ
- ห้ามมี Business Logic

```python
# ✅ ถูกต้อง
class BookingRepository:
    async def find_conflicts(self, room_id: int, start: datetime, end: datetime) -> list[Booking]:
        stmt = (
            select(Booking)
            .where(
                Booking.room_id == room_id,
                Booking.status.in_(["pending", "confirmed"]),
                Booking.start_time < end,
                Booking.end_time > start,
            )
            .with_for_update()  # ← DB-level lock ป้องกัน Race Condition
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
```

---

## 4. Frontend Architecture

### 4.1 Setup Command

```bash
# 1. Scaffold Vue project (เลือก: TypeScript, Vue Router, Pinia, Vitest, ESLint)
npm create vue@latest frontend

# 2. Install TailwindCSS v4 + DaisyUI v5
cd frontend
npm install tailwindcss@latest @tailwindcss/vite@latest daisyui@latest
```

**หมายเหตุ TailwindCSS v4:** ไม่มี `tailwind.config.js` อีกต่อไป — config ทั้งหมดอยู่ใน `src/assets/main.css`

```css
/* src/assets/main.css */
@import "tailwindcss";
@plugin "daisyui";
```

```typescript
// vite.config.ts — เพิ่ม Tailwind Vite plugin
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
})
```

### 4.2 Directory Structure

```
frontend/src/
├── assets/
│   └── main.css          ← @import "tailwindcss" + @plugin "daisyui"
├── components/           ← Pure (reusable) components
│   ├── common/           ← AppButton, AppInput, AppModal, AppBadge
│   ├── booking/          ← TimeSlotPicker, BookingCard, StatusBadge
│   └── room/             ← RoomCard, RoomCalendar
├── composables/          ← Reusable logic (useBooking, useAuth, useNotification)
├── layouts/              ← AppLayout, AdminLayout, AuthLayout
├── pages/                ← Route-level components (Smart)
│   ├── auth/             ← LoginPage, RegisterPage
│   ├── member/           ← DashboardPage, BookingPage, MyBookingsPage
│   ├── approver/         ← PendingApprovalsPage
│   └── admin/            ← AdminDashboard, RoomsPage, UsersPage, SettingsPage
├── router/               ← Vue Router + Navigation Guards (role-based)
├── services/             ← API call functions (bookingService, roomService)
├── stores/               ← Pinia stores (authStore, bookingStore, roomStore)
├── types/                ← TypeScript interfaces + Zod schemas
└── utils/                ← Helper functions
```

### 4.2 Component Rules

```
Pages (Smart)          ← อ่าน Store, เรียก Service ผ่าน Store
    │
    └── Components (Pure) ← รับ props, emit events, ไม่รู้จัก Store
            │
            └── ❌ ห้าม call API โดยตรง
```

### 4.3 Auth Flow (Frontend)

```
Login Form
    │
    ▼
authStore.login(email, password)
    │
    ▼
authService.login() → POST /api/v1/auth/login
    │
    ▼
เก็บ JWT ใน memory (authStore.token)
    │
    ▼
axios interceptor แนบ Authorization: Bearer {token} ทุก request
    │
    ▼
Vue Router Guard ตรวจ role ก่อนเข้าแต่ละ route
```

---

## 5. Database Architecture

### 5.1 Tables Overview

```
┌──────────┐     ┌──────────┐     ┌──────────────┐
│  users   │────<│ bookings │>────│    rooms     │
└──────────┘     └──────────┘     └──────────────┘
     │                │                   │
     │           ┌────▼──────┐      ┌─────▼──────┐
     │           │  booking  │      │   room_    │
     │           │  snapshot │      │  equipment │
     │           └───────────┘      └────────────┘
     │
┌────▼──────────┐     ┌──────────────────┐
│ notifications │     │   audit_logs     │
└───────────────┘     └──────────────────┘
                       ┌──────────────────┐
                       │  system_configs  │
                       └──────────────────┘
```

### 5.2 Booking Conflict Prevention Strategy

```
Transaction Begin
    │
    ├─ SELECT * FROM bookings
    │  WHERE room_id = ?
    │  AND status IN ('pending','confirmed')
    │  AND start_time < ? AND end_time > ?
    │  FOR UPDATE          ← Row-level lock
    │
    ├─ มี conflict? → Raise ConflictError → Rollback
    │
    └─ ไม่มี conflict? → INSERT booking → Commit
```

---

## 6. API Architecture

### 6.1 Base URL Structure

```
/api/v1/auth/         ← Authentication (public)
/api/v1/rooms/        ← Room search & detail (authenticated)
/api/v1/bookings/     ← Booking CRUD (authenticated)
/api/v1/approvals/    ← Approval actions (approver+)
/api/v1/users/me      ← Current user profile (authenticated)
/api/v1/admin/        ← Admin operations (admin only)
/api/v1/notifications/← Notifications (authenticated)
/health               ← Health check (public)
```

### 6.2 Authentication Strategy

```
Request
    │
    ▼
FastAPI Dependency: get_current_user()
    │
    ├─ ดึง token จาก Header: Authorization: Bearer {token}
    ├─ Decode JWT → user_id, role, exp
    ├─ ตรวจ exp หมดอายุ?
    ├─ ดึง user จาก DB → ตรวจ status = 'active'?
    └─ คืน CurrentUser object

Role Check (ถัดจาก get_current_user):
    get_current_active_user()   ← role: member, approver, admin
    require_approver()          ← role: approver, admin
    require_admin()             ← role: admin เท่านั้น
```

### 6.3 Standard Response Format

```json
// Success
{
  "data": { ... },
  "message": "success"
}

// Error
{
  "detail": "error message",
  "code": "BOOKING_CONFLICT"
}

// Paginated List
{
  "data": [ ... ],
  "total": 100,
  "page": 1,
  "per_page": 20
}
```

---

## 7. Security Architecture

### 7.1 Role-Based Access Control (RBAC)

```
Role Hierarchy:
admin > approver > member

Permissions:
┌────────────────────────────┬────────┬──────────┬───────┐
│ Action                     │ Member │ Approver │ Admin │
├────────────────────────────┼────────┼──────────┼───────┤
│ Register / Login           │   ✅   │    ✅    │  ✅   │
│ Search & View rooms        │   ✅   │    ✅    │  ✅   │
│ Create booking             │   ✅   │    ✅    │  ✅   │
│ Cancel own booking         │   ✅   │    ✅    │  ✅   │
│ View own bookings          │   ✅   │    ✅    │  ✅   │
│ View all pending bookings  │   ❌   │    ✅    │  ✅   │
│ Approve / Reject booking   │   ❌   │    ✅    │  ✅   │
│ Cancel any booking         │   ❌   │    ❌    │  ✅   │
│ Manage rooms               │   ❌   │    ❌    │  ✅   │
│ Manage users               │   ❌   │    ❌    │  ✅   │
│ Approve member registration│   ❌   │    ❌    │  ✅   │
│ Assign approver role       │   ❌   │    ❌    │  ✅   │
│ System configuration       │   ❌   │    ❌    │  ✅   │
│ View audit logs            │   ❌   │    ❌    │  ✅   │
│ View dashboard             │   ❌   │    ❌    │  ✅   │
└────────────────────────────┴────────┴──────────┴───────┘
```

---

## 8. Deployment Architecture

### 8.1 Development

```
┌─────────────────┐        ┌─────────────────┐
│   Frontend      │        │    Backend      │
│ localhost:5173  │◄──────►│ localhost:8000  │
│  npm run dev    │  CORS  │ uvicorn --reload│
└─────────────────┘        └────────┬────────┘
                                    │
                           ┌────────▼────────┐
                           │  SQLite File    │
                           │ data/booking.db │
                           └─────────────────┘
```

### 8.2 Production-Ready Path

```
┌─────────────────┐        ┌─────────────────┐
│   Frontend      │        │    Backend      │
│  Nginx (static) │◄──────►│ Gunicorn+Uvicorn│
│  dist/ folder   │  Proxy │  workers        │
└─────────────────┘        └────────┬────────┘
                                    │
                           ┌────────▼────────┐
                           │   PostgreSQL    │
                           └─────────────────┘
```

### 8.3 Standalone Executable (PyInstaller)

```
┌─────────────────┐        ┌─────────────────┐
│   Frontend      │        │    Backend      │
│  Nginx / CDN    │◄──────►│  booking_api.exe│
│                 │        │ (PyInstaller)   │
└─────────────────┘        └────────┬────────┘
                                    │
                           ┌────────▼────────┐
                           │ Database (Any)  │
                           └─────────────────┘
```
- รองรับการใช้ **PyInstaller** เพื่อแพ็ค FastAPI + Dependencies ทั้งหมดเป็นไฟล์เดียว (`.exe` หรือ binary)
- ช่วยลดความยุ่งยากในการติดตั้ง Python และ Environment บนเครื่อง On-Premise Server ขององค์กร

---

## 9. Backend Directory Structure

```
backend/
├── app/
│   ├── main.py                    ← FastAPI app, CORS, include routers
│   ├── api/
│   │   └── v1/
│   │       ├── router.py          ← รวม all routers
│   │       └── endpoints/
│   │           ├── auth.py        ← /auth/register, /auth/login
│   │           ├── rooms.py       ← /rooms GET, POST, PUT
│   │           ├── bookings.py    ← /bookings CRUD
│   │           ├── approvals.py   ← /approvals/pending, approve, reject
│   │           ├── users.py       ← /users/me
│   │           ├── admin.py       ← /admin/* (users, config, dashboard)
│   │           └── notifications.py
│   ├── core/
│   │   ├── config.py              ← Settings (pydantic-settings)
│   │   ├── database.py            ← Async engine, session factory
│   │   ├── deps.py                ← FastAPI Dependencies (get_current_user, require_admin)
│   │   └── security.py            ← JWT encode/decode, password hash
│   ├── models/                    ← SQLAlchemy ORM models
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── room.py
│   │   ├── booking.py
│   │   ├── notification.py
│   │   ├── audit_log.py
│   │   └── system_config.py
│   ├── schemas/                   ← Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── room.py
│   │   ├── booking.py
│   │   ├── notification.py
│   │   └── common.py              ← PaginatedResponse, StandardResponse
│   ├── services/                  ← Business Logic
│   │   ├── auth_service.py
│   │   ├── room_service.py
│   │   ├── booking_service.py
│   │   ├── user_service.py
│   │   ├── notification_service.py
│   │   └── config_service.py
│   └── repositories/              ← Database queries
│       ├── base.py
│       ├── user_repository.py
│       ├── room_repository.py
│       ├── booking_repository.py
│       ├── notification_repository.py
│       └── audit_repository.py
├── alembic/                       ← Database migrations
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py                ← Shared fixtures (test DB, test client)
│   ├── test_auth.py
│   ├── test_bookings.py           ← Conflict check tests
│   └── test_rooms.py
├── data/                          ← SQLite file (dev only)
├── .env.example
└── requirements.txt
```

---

## 10. Coding Standards

| ด้าน | Standard | รายละเอียด |
|---|---|---|
| **Frontend Language** | TypeScript (strict) | ทุกไฟล์ `.ts` / `.vue` ต้องมี type annotation ครบ ห้ามใช้ `any` |
| **Frontend Style** | Vue 3 Composition API | ใช้ `<script setup lang="ts">` ทุกไฟล์ ห้ามใช้ Options API |
| **Backend Language** | Python + Type Hints | ทุก function ต้องมี parameter type และ return type เสมอ |
| **Backend Schema** | Pydantic v2 | ใช้แทน `dict` ในการรับ/ส่งข้อมูลทุกจุด |
| **Backend Async** | async/await | ทุก endpoint และ service method เป็น async |

### ตัวอย่าง Python Type Hints (Backend)

```python
# ✅ ถูกต้อง — มี type hints ครบ
async def get_booking(
    booking_id: int,
    current_user: CurrentUser,
    db: AsyncSession,
) -> BookingResponse:
    ...

# ❌ ผิด — ไม่มี type hints
async def get_booking(booking_id, current_user, db):
    ...
```

### ตัวอย่าง Vue Composition API (Frontend)

```vue
<!-- ✅ ถูกต้อง — <script setup lang="ts"> -->
<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Booking } from '@/types/booking'

const props = defineProps<{ booking: Booking }>()
const isExpired = computed(() => new Date(props.booking.end_time) < new Date())
</script>

<!-- ❌ ผิด — Options API -->
<script lang="ts">
export default { data() { return {} } }
</script>
```

---

## 11. Architecture Decision Summary

| การตัดสินใจ | ทางเลือกที่เลือก | เหตุผล |
|---|---|---|
| Architecture Pattern | Monolith + Strict Layers | Simple, maintainable, YAGNI |
| Frontend Scaffolding | `npm create vue@latest` | Official Vue tool — Vue Router + Pinia พร้อมใน 1 คำสั่ง |
| CSS Framework | TailwindCSS v4 + @tailwindcss/vite | ไม่ต้อง PostCSS config, Vite-native |
| UI Components | DaisyUI v5 | Built for Tailwind v4, theme + component library |
| Database (dev) | SQLite + aiosqlite | Zero config, เริ่มเร็ว |
| Database (prod) | MySQL / MariaDB / PostgreSQL | เปลี่ยนได้ผ่าน `DATABASE_URL` ใน `.env` เท่านั้น |
| ORM | SQLAlchemy 2 async | Abstract database — switch ได้โดยไม่แตะโค้ด |
| Auth | JWT + DB status check | Stateless token แต่ตรวจ user.status ทุก request → revoke ได้ทันที |
| State Management | Pinia | Official Vue 3 store, TypeScript-first |
| Conflict Prevention | `SELECT FOR UPDATE` | Database-level guarantee, ไม่ต้องการ Redis |
---

## 12. Validation & Error Handling Flow

ระบบใช้กลยุทธ์ **"Multi-layered Validation"** เพื่อความปลอดภัยสูงสุดและ UX ที่ดีที่สุด

### 12.1 Validation Layers

1.  **Client-Side (Immediate UX)**:
    *   ใช้ **HTML5 Constraints** และ **Vee-Validate/Zod** ในการตรวจสอบเบื้องต้น
    *   *วัตถุประสงค์:* ลดจำนวน Request ที่ไม่จำเป็นและให้ Feedback แก่ผู้ใช้ทันที
2.  **API Schema Layer (Syntactic Check)**:
    *   ใช้ **Pydantic** ในการตรวจสอบโครงสร้างข้อมูล (Types, Range, Enum)
    *   *วัตถุประสงค์:* มั่นใจว่าข้อมูลที่เข้าสู่ Service Layer มีโครงสร้างที่ถูกต้อง
3.  **Service Layer (Business Logic Check)**:
    *   ตรวจสอบกฎทางธุรกิจที่ซับซ้อน (เช่น ข้อมูลซ้ำ, ตารางเวลาชนกัน)
    *   *วัตถุประสงค์:* รักษาความถูกต้องของกฎทางธุรกิจ (Business Integrity)
4.  **Database Layer (Data Integrity)**:
    *   ใช้ **Constraints, Unique Index, Foreign Keys**
    *   *วัตถุประสงค์:* เป็นปราการด่านสุดท้ายป้องกันข้อมูลเน่าเสีย (Data Corruption)

### 12.2 Unified Error Handling Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Service
    participant Database

    User->>Frontend: Submit Form
    Frontend->>Frontend: Client-side Validation
    Note right of Frontend: If fail, show local error

    Frontend->>API: POST /resource (JSON)
    API->>API: Pydantic Schema Check
    Note right of API: If fail, return 422 Standard Error

    API->>Service: Execute Business Logic
    Service->>Database: Query/Check
    Note right of Service: If business rule fail, raise HTTPException

    Service->>Database: Commit Transaction
    Database-->>Service: Success
    Service-->>API: Result Object
    API-->>Frontend: 200/201 Success (Standard Format)
    Frontend-->>User: Show Success Notification
```

> [!IMPORTANT]
> ทุก Error ต้องผ่าน **Global Exception Handler** เพื่อแปลงให้เป็นรูปแบบมาตรฐาน (Flat JSON) ที่ระบุไว้ใน `14_error_handling_and_logging.md` เพื่อให้ Frontend สามารถจัดการข้อความแจ้งเตือนได้อย่างสม่ำเสมอ
