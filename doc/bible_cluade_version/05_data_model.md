# 05 — Data Model

---

## 1. ER Diagram (Overview)

```
┌─────────────────┐         ┌──────────────────────┐         ┌─────────────────┐
│      users      │         │       bookings        │         │      rooms      │
├─────────────────┤         ├──────────────────────┤         ├─────────────────┤
│ PK id           │──────1──│ FK user_id            │──M──────│ PK id           │
│    email        │         │ FK room_id            │         │    name         │
│    password_hash│         │    title              │         │    capacity     │
│    employee_code│         │    description        │         │    location     │
│    full_name    │         │    start_time         │         │    building     │
│    department   │         │    end_time           │         │    floor        │
│    phone        │         │    attendee_count     │         │    description  │
│    role         │         │    status             │         │    status       │
│    status       │         │    ── Snapshot ──     │         │    created_at   │
│    created_at   │         │    snap_room_name     │         │    updated_at   │
│    updated_at   │         │    snap_room_capacity │         └────────┬────────┘
└────────┬────────┘         │    snap_room_location │                  │
         │                  │    snap_user_name     │         ┌────────▼────────┐
         │                  │    snap_user_dept     │         │  room_images    │
         │                  │    snap_user_email    │         ├─────────────────┤
         │                  │    created_at         │         │ PK id           │
         │                  │    updated_at         │         │ FK room_id      │
         │                  └───────────┬───────────┘         │    image_path   │
         │                              │                      │    is_primary   │
         │                  ┌───────────▼───────────┐         │    created_at   │
         │                  │   booking_approvals   │         └─────────────────┘
         │                  ├──────────────────────┤
         │                  │ PK id                │         ┌─────────────────┐
         │                  │ FK booking_id (uniq) │         │ room_equipment  │
         │──────────────────│ FK approver_id       │         ├─────────────────┤
         │                  │    action            │         │ PK id           │
         │                  │    reason            │         │ FK room_id      │
         │                  │    actioned_at       │         │    name         │
         │                  └───────────────────────┘         └─────────────────┘

┌─────────────────────────┐         ┌──────────────────────┐
│      notifications      │         │      audit_logs      │
├─────────────────────────┤         ├──────────────────────┤
│ PK id                   │         │ PK id                │
│ FK user_id              │         │ FK user_id (nullable)│
│ FK booking_id (nullable)│         │    action            │
│    type                 │         │    entity_type       │
│    message              │         │    entity_id         │
│    is_read              │         │    old_value (JSON)  │
│    created_at           │         │    new_value (JSON)  │
└─────────────────────────┘         │    ip_address        │
                                    │    created_at        │
┌─────────────────────────┐         └──────────────────────┘
│     system_configs      │
├─────────────────────────┤
│ PK id                   │
│    key (unique)         │
│    value                │
│    description          │
│ FK updated_by           │
│    updated_at           │
└─────────────────────────┘
```

---

## 2. Table Definitions

---

### 2.1 `users`

ข้อมูลสมาชิกทุกประเภท (Member, Approver, Admin) เก็บในตารางเดียว แยกด้วย `role`

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO INCREMENT | Primary key |
| `email` | VARCHAR(255) | NOT NULL, UNIQUE | Email ใช้ Login |
| `password_hash` | VARCHAR(255) | NOT NULL | bcrypt hash — ห้าม plain text |
| `employee_code` | VARCHAR(50) | NOT NULL, UNIQUE | รหัสพนักงาน |
| `full_name` | VARCHAR(255) | NOT NULL | ชื่อ-นามสกุล |
| `department` | VARCHAR(255) | NOT NULL | หน่วยงาน |
| `phone` | VARCHAR(20) | NULLABLE | เบอร์โทรศัพท์ |
| `role` | ENUM | NOT NULL, DEFAULT `member` | `member` / `approver` / `admin` |
| `status` | ENUM | NOT NULL, DEFAULT `pending` | `pending` / `active` / `suspended` / `rejected` / `deleted` |
| `created_at` | DATETIME | NOT NULL, DEFAULT now() | วันที่สมัคร |
| `updated_at` | DATETIME | NOT NULL, DEFAULT now() | วันที่แก้ไขล่าสุด |

**Indexes:** `email` (UNIQUE), `employee_code` (UNIQUE), `status`, `role`

**Business Rules:**
- `status = pending` → ยัง Login ไม่ได้
- `status = suspended` → Login ไม่ได้และจองใหม่ไม่ได้
- `status = deleted` → (Soft Delete ตาม PDPA) ข้อมูลถูกทำเป็นนิรนาม (Anonymized) และไม่สามารถ Login ได้
- `role` เปลี่ยนได้เฉพาะ Admin เท่านั้น

---

### 2.2 `rooms`

ข้อมูลห้องประชุมทั้งหมด

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO INCREMENT | Primary key |
| `name` | VARCHAR(255) | NOT NULL | ชื่อห้อง |
| `capacity` | INTEGER | NOT NULL | ความจุสูงสุด (คน) |
| `location` | VARCHAR(255) | NOT NULL | สถานที่ (เช่น อาคาร A) |
| `building` | VARCHAR(100) | NULLABLE | ชื่ออาคาร |
| `floor` | VARCHAR(20) | NULLABLE | ชั้น |
| `description` | TEXT | NULLABLE | คำอธิบายเพิ่มเติม |
| `status` | ENUM | NOT NULL, DEFAULT `active` | `active` / `inactive` |
| `created_at` | DATETIME | NOT NULL, DEFAULT now() | — |
| `updated_at` | DATETIME | NOT NULL, DEFAULT now() | — |

**Indexes:** `status`

**Business Rules:**
- `status = inactive` → ไม่ปรากฏในผลค้นหา
- ลบห้องไม่ได้ — ใช้ `status = inactive` แทน
- **Business Rule:** ชื่อห้อง (`name`) ต้องไม่ซ้ำกันภายใต้อาคาร (`building`) เดียวกัน

---

### 2.3 `room_images`

รูปภาพของห้องประชุม (1 ห้อง มีได้หลายรูป)

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO INCREMENT | — |
| `room_id` | INTEGER | FK → rooms.id, NOT NULL | ห้องที่รูปนี้สังกัด |
| `image_path` | VARCHAR(500) | NOT NULL | Path ของไฟล์รูปใน server |
| `is_primary` | BOOLEAN | NOT NULL, DEFAULT false | รูปหลักที่แสดงใน Card |
| `created_at` | DATETIME | NOT NULL, DEFAULT now() | — |

**Constraint:** แต่ละห้องมี `is_primary = true` ได้ **1 รูปเท่านั้น**

---

### 2.4 `room_equipment`

อุปกรณ์ในห้องประชุม (1 ห้อง มีได้หลายอุปกรณ์)

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO INCREMENT | — |
| `room_id` | INTEGER | FK → rooms.id, NOT NULL | ห้องที่อุปกรณ์นี้อยู่ |
| `name` | VARCHAR(100) | NOT NULL | เช่น `projector`, `whiteboard`, `tv`, `microphone` |

---

### 2.5 `bookings`

หัวใจของระบบ — บันทึกการจองพร้อม Snapshot

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO INCREMENT | — |
| `room_id` | INTEGER | FK → rooms.id, NOT NULL | ห้องที่จอง (FK สำหรับ query) |
| `user_id` | INTEGER | FK → users.id, NOT NULL | ผู้จอง (FK สำหรับ query) |
| `title` | VARCHAR(255) | NOT NULL | หัวข้อการประชุม |
| `description` | TEXT | NULLABLE | รายละเอียดเพิ่มเติม |
| `start_time` | DATETIME | NOT NULL | เวลาเริ่มต้น |
| `end_time` | DATETIME | NOT NULL | เวลาสิ้นสุด |
| `attendee_count` | INTEGER | NOT NULL | จำนวนผู้เข้าร่วมโดยประมาณ |
| `status` | ENUM | NOT NULL, DEFAULT `pending` | `pending` / `confirmed` / `rejected` / `cancelled` |
| `cancel_reason` | TEXT | NULLABLE | เหตุผลการยกเลิก (ถ้า cancelled) |
| `cancelled_by` | INTEGER | FK → users.id, NULLABLE | ใครเป็นคนยกเลิก |
| **── Snapshot ──** | | | ข้อมูลที่ตรึงไว้ ณ เวลาจอง |
| `snap_room_name` | VARCHAR(255) | NOT NULL | ชื่อห้อง ณ วันที่จอง |
| `snap_room_capacity` | INTEGER | NOT NULL | ความจุ ณ วันที่จอง |
| `snap_room_location` | VARCHAR(255) | NOT NULL | สถานที่ ณ วันที่จอง |
| `snap_user_name` | VARCHAR(255) | NOT NULL | ชื่อผู้จอง ณ วันที่จอง |
| `snap_user_department` | VARCHAR(255) | NOT NULL | หน่วยงาน ณ วันที่จอง |
| `snap_user_email` | VARCHAR(255) | NOT NULL | Email ณ วันที่จอง |
| `created_at` | DATETIME | NOT NULL, DEFAULT now() | — |
| `updated_at` | DATETIME | NOT NULL, DEFAULT now() | — |

**Indexes:** `room_id + start_time + end_time + status` (Composite — สำหรับ Conflict Check), `user_id`, `status`

**Business Rules:**
- Snapshot fields ต้องถูก populate ทุกครั้งที่สร้าง Booking — ห้าม null
- `status = confirmed / rejected` → แก้ไขไม่ได้ เฉพาะ cancel ได้
- Conflict Check: ต้องไม่มี booking อื่นที่ `room_id` เดียวกัน, `status IN (pending, confirmed)`, และ time range ซ้อนกัน

**Conflict Detection Query:**
```sql
SELECT id FROM bookings
WHERE room_id = :room_id
  AND status IN ('pending', 'confirmed')
  AND start_time < :end_time
  AND end_time > :start_time
FOR UPDATE;
```

---

### 2.6 `booking_approvals`

บันทึกการ Approve/Reject ของ Approver (1 booking มี 1 approval record)

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO INCREMENT | — |
| `booking_id` | INTEGER | FK → bookings.id, NOT NULL, UNIQUE | หนึ่ง Booking มีได้ 1 record |
| `approver_id` | INTEGER | FK → users.id, NOT NULL | Approver ที่ดำเนินการ |
| `action` | ENUM | NOT NULL | `approved` / `rejected` |
| `reason` | TEXT | NULLABLE | เหตุผล (บังคับกรอกเมื่อ `rejected`) |
| `actioned_at` | DATETIME | NOT NULL, DEFAULT now() | เวลาที่ดำเนินการ |

**Business Rules:**
- สร้าง record นี้เมื่อ Approver กด Approve หรือ Reject เท่านั้น
- `reason` บังคับมีค่าเมื่อ `action = rejected`

---

### 2.7 `notifications`

การแจ้งเตือนภายในระบบ (In-app)

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO INCREMENT | — |
| `user_id` | INTEGER | FK → users.id, NOT NULL | ผู้รับ notification |
| `booking_id` | INTEGER | FK → bookings.id, NULLABLE | Booking ที่เกี่ยวข้อง |
| `type` | ENUM | NOT NULL | ดูด้านล่าง |
| `message` | TEXT | NOT NULL | ข้อความแจ้งเตือน |
| `is_read` | BOOLEAN | NOT NULL, DEFAULT false | อ่านแล้วหรือยัง |
| `created_at` | DATETIME | NOT NULL, DEFAULT now() | — |

**Notification Types:**
| Type | ส่งถึง | เมื่อ |
|---|---|---|
| `booking_confirmed` | Member | Approver อนุมัติ booking ของ Member |
| `booking_rejected` | Member | Approver ปฏิเสธ booking ของ Member |
| `booking_cancelled` | Member | Admin ยกเลิก booking ของ Member |
| `new_booking_pending` | Approver | มี booking ใหม่รอการอนุมัติ |
| `user_approved` | Member | Admin อนุมัติการสมัครสมาชิก |
| `user_rejected` | Member | Admin ปฏิเสธการสมัครสมาชิก |

**Indexes:** `user_id + is_read`, `created_at`

**Data Retention Policy:** ระบบจะลบ Notification ที่ตั้งค่าเป็น `is_read = true` และมีอายุเก่ากว่า 90 วันโดยอัตโนมัติ

---

### 2.8 `audit_logs`

บันทึกทุกการกระทำสำคัญในระบบ (Immutable — ไม่มีการแก้ไขหรือลบ)

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO INCREMENT | — |
| `user_id` | INTEGER | FK → users.id, NULLABLE | ผู้กระทำ (null = system) |
| `action` | VARCHAR(100) | NOT NULL | เช่น `booking.create`, `user.approve`, `room.deactivate` |
| `entity_type` | VARCHAR(50) | NOT NULL | เช่น `booking`, `user`, `room` |
| `entity_id` | INTEGER | NOT NULL | ID ของ record ที่ถูกกระทำ |
| `old_value` | JSON | NULLABLE | ค่าก่อนเปลี่ยน |
| `new_value` | JSON | NULLABLE | ค่าหลังเปลี่ยน |
| `ip_address` | VARCHAR(45) | NULLABLE | IPv4 / IPv6 |
| `created_at` | DATETIME | NOT NULL, DEFAULT now() | — |

**Audit Actions ที่ต้องบันทึกเสมอ:**
| Action | Entity |
|---|---|
| `user.register` | user |
| `user.login` | user |
| `user.login_failed` | user |
| `user.approve` / `user.reject` | user |
| `user.suspend` / `user.reactivate` | user |
| `user.role_change` | user |
| `booking.create` | booking |
| `booking.confirm` / `booking.reject` | booking |
| `booking.cancel` | booking |
| `room.create` / `room.update` | room |
| `room.deactivate` / `room.activate` | room |
| `config.update` | system_config |

**Indexes:** `user_id`, `entity_type + entity_id`, `created_at`

**Data Retention Policy:** Audit logs ที่มีอายุเกิน 1 ปี จะถูก Archive ออกจากฐานข้อมูลหลัก เพื่อลดภาระ (Performance) ของ Database

---

### 2.9 `system_configs`

ตั้งค่ากฎการจองของระบบ — Admin แก้ไขได้ผ่าน UI โดยไม่ต้อง Deploy

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PK, AUTO INCREMENT | — |
| `key` | VARCHAR(100) | NOT NULL, UNIQUE | ชื่อ config key |
| `value` | VARCHAR(500) | NOT NULL | ค่า (เก็บเป็น string, แปลง type ตอนใช้) |
| `description` | TEXT | NULLABLE | คำอธิบายสำหรับ Admin |
| `updated_by` | INTEGER | FK → users.id, NULLABLE | Admin คนสุดท้ายที่แก้ |
| `updated_at` | DATETIME | NOT NULL, DEFAULT now() | — |

**Default Config Values:**

| Key | Default Value | Description |
|---|---|---|
| `max_advance_days` | `30` | จองล่วงหน้าได้สูงสุด (วัน) |
| `max_booking_hours` | `4` | ระยะเวลาจองสูงสุดต่อครั้ง (ชั่วโมง) |
| `max_bookings_per_day` | `3` | Member จองได้สูงสุดต่อวัน (ครั้ง) |

---

## 3. Relationships Summary

| From | Relationship | To | Notes |
|---|---|---|---|
| `users` | 1 : M | `bookings` | user เป็นผู้จอง |
| `rooms` | 1 : M | `bookings` | booking อ้างอิงห้อง |
| `bookings` | 1 : 0..1 | `booking_approvals` | pending booking ยังไม่มี approval |
| `users` | 1 : M | `booking_approvals` | user เป็น approver |
| `rooms` | 1 : M | `room_images` | ห้องมีหลายรูป |
| `rooms` | 1 : M | `room_equipment` | ห้องมีหลายอุปกรณ์ |
| `users` | 1 : M | `notifications` | user รับหลาย notification |
| `bookings` | 1 : M | `notifications` | booking trigger notification |
| `users` | 1 : M | `audit_logs` | user กระทำหลาย action |
| `users` | 1 : M | `system_configs` | admin update config |

---

## 4. Enum Definitions

```python
# Python (SQLAlchemy Enum)

class UserRole(str, Enum):
    MEMBER = "member"
    APPROVER = "approver"
    ADMIN = "admin"

class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REJECTED = "rejected"
    DELETED = "deleted"

class RoomStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class ApprovalAction(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"

class NotificationType(str, Enum):
    BOOKING_CONFIRMED = "booking_confirmed"
    BOOKING_REJECTED = "booking_rejected"
    BOOKING_CANCELLED = "booking_cancelled"
    NEW_BOOKING_PENDING = "new_booking_pending"
    USER_APPROVED = "user_approved"
    USER_REJECTED = "user_rejected"
```

```typescript
// TypeScript (Frontend)

export type UserRole = 'member' | 'approver' | 'admin'
export type UserStatus = 'pending' | 'active' | 'suspended' | 'rejected' | 'deleted'
export type RoomStatus = 'active' | 'inactive'
export type BookingStatus = 'pending' | 'confirmed' | 'rejected' | 'cancelled'
export type ApprovalAction = 'approved' | 'rejected'
export type NotificationType =
  | 'booking_confirmed'
  | 'booking_rejected'
  | 'booking_cancelled'
  | 'new_booking_pending'
  | 'user_approved'
  | 'user_rejected'
```

---

## 5. Snapshot Pattern — Why

```
สถานการณ์จริง:

วันที่ 1 มกราคม:
  - ห้อง "ห้องประชุม A" ความจุ 10 คน
  - สมาชิก "สมชาย ใจดี" หน่วยงาน "IT"
  - จองห้องสำเร็จ → booking_id = 42

วันที่ 15 มกราคม:
  - ห้องถูกเปลี่ยนชื่อเป็น "ห้องประชุม Executive"
  - สมชายย้ายหน่วยงานไป "Finance"

ถามว่า booking_id = 42 ควรแสดงข้อมูลอะไร?
→ ✅ ต้องแสดงข้อมูล ณ วันจอง: "ห้องประชุม A", "IT"
→ ❌ ถ้าใช้แค่ FK จะแสดง: "ห้องประชุม Executive", "Finance" ← ผิด
```

**Snapshot fields ต้อง populate ทันทีตอนสร้าง Booking:**

```python
# booking_service.py
async def create(self, user: CurrentUser, data: BookingCreate) -> Booking:
    room = await self.room_repo.get_by_id(data.room_id)

    new_booking = Booking(
        room_id=data.room_id,
        user_id=user.id,
        title=data.title,
        start_time=data.start_time,
        end_time=data.end_time,
        attendee_count=data.attendee_count,
        # Snapshot — ตรึงข้อมูล ณ เวลานี้
        snap_room_name=room.name,
        snap_room_capacity=room.capacity,
        snap_room_location=room.location,
        snap_user_name=user.full_name,
        snap_user_department=user.department,
        snap_user_email=user.email,
    )
    return await self.booking_repo.create(new_booking)
```

---

## 6. Database Driver & Connection

### Async Driver ตาม Database ที่เลือก

| Database | Package | `DATABASE_URL` format |
|---|---|---|
| SQLite (dev) | `aiosqlite` (มีใน requirements.txt แล้ว) | `sqlite+aiosqlite:///./data/bookingme.db` |
| MySQL / MariaDB | `pip install aiomysql` | `mysql+aiomysql://user:pass@host:3306/dbname` |
| PostgreSQL | `pip install asyncpg` | `postgresql+asyncpg://user:pass@host:5432/dbname` |

**เปลี่ยน Database = เปลี่ยนแค่ `DATABASE_URL` ใน `.env` + ติดตั้ง driver ที่ตรงกัน**
โค้ด SQLAlchemy ORM ทุกส่วนไม่ต้องแก้ไข

### ข้อควรระวังเมื่อ Switch Database

| ประเด็น | SQLite | MySQL/MariaDB | PostgreSQL |
|---|---|---|---|
| `SELECT FOR UPDATE` | ❌ ไม่รองรับ (ใช้ transaction lock แทน) | ✅ รองรับ | ✅ รองรับ |
| JSON column | ✅ (stored as text) | ✅ | ✅ |
| ENUM type | ✅ | ✅ | ต้องใช้ `VARCHAR` หรือสร้าง PG Enum |
| Case sensitivity | ❌ case-insensitive | depends on collation | ✅ case-sensitive |

> **สำหรับ dev (SQLite):** Conflict Check ใช้ Transaction isolation แทน `FOR UPDATE`
> **สำหรับ prod (MySQL/PostgreSQL):** ใช้ `.with_for_update()` ได้เต็มที่

---

## 7. Migration Strategy (Alembic)

```
alembic/versions/
├── 001_create_users.py
├── 002_create_rooms_and_equipment.py
├── 003_create_bookings.py
├── 004_create_booking_approvals.py
├── 005_create_notifications.py
├── 006_create_audit_logs.py
├── 007_create_system_configs.py
└── 008_seed_default_configs.py   ← seed ค่า default ของ system_configs
```

**กฎ Migration:**
- ห้ามแก้ไข migration file ที่ถูก apply ไปแล้ว — สร้าง migration ใหม่แทน
- ทุก migration ต้องมีทั้ง `upgrade()` และ `downgrade()`
- `008_seed_default_configs.py` สร้าง default system_configs ทันทีหลัง create table
- Migration ต้องทดสอบได้ทั้งบน SQLite (dev) และ MySQL/PostgreSQL (prod)
