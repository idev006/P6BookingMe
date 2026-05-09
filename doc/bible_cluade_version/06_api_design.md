# 06 — API Design

---

## 1. API Conventions

### Base URL
```
Development : http://localhost:8000/api/v1
Production  : https://domain.com/api/v1
```

### Authentication
ทุก endpoint ยกเว้น `[PUBLIC]` ต้องส่ง Header:
```
Authorization: Bearer <JWT_TOKEN>
```

### Timezone Convention (UTC-First)
- ทุก API ต้องรับ-ส่งข้อมูลวันที่และเวลาเป็น **UTC (ISO-8601)** เสมอ โดยลงท้ายด้วย `Z` (เช่น `2026-05-10T09:00:00Z`)
- ห้ามรับ-ส่งเวลาแบบ Local Time เด็ดขาด
- Frontend (Vue) จะรับหน้าที่แปลงเวลา UTC เป็น Local Time ตามเบราว์เซอร์ของผู้ใช้ก่อนแสดงผล

### Standard Response Format

```json
// ✅ Success — single object
{
  "data": { ... },
  "message": "success"
}

// ✅ Success — list with pagination
{
  "data": [ ... ],
  "total": 100,
  "page": 1,
  "per_page": 20
}

// ❌ Error
{
  "detail": "Human-readable error message",
  "error_code": "ERROR_CODE",
  "path": "/api/v1/resource"
}
```

### HTTP Status Codes

| Code | ใช้เมื่อ |
|---|---|
| `200` | GET / PUT สำเร็จ |
| `201` | POST สร้างข้อมูลใหม่สำเร็จ |
| `204` | DELETE / action สำเร็จ (ไม่มี body) |
| `400` | Request body ผิด format / validation fail |
| `401` | ไม่มี token หรือ token หมดอายุ |
| `403` | มี token แต่ไม่มีสิทธิ์ (role ไม่พอ) |
| `404` | ไม่พบ resource |
| `409` | Conflict — เช่น จองห้องซ้อนกัน, email ซ้ำ |
| `422` | Unprocessable Entity — Pydantic validation error |
| `500` | Server error |

### Error Codes

| Code | HTTP | ความหมาย |
|---|---|---|
| `BOOKING_CONFLICT` | 409 | ช่วงเวลาจองซ้อนกับการจองอื่น |
| `ROOM_INACTIVE` | 400 | ห้องถูกปิดการใช้งาน |
| `BOOKING_RULE_VIOLATION` | 400 | ละเมิดกฎการจอง (เกินจำนวนครั้ง/ชั่วโมง) |
| `INVALID_TIME_RANGE` | 400 | เวลาเริ่มต้น >= เวลาสิ้นสุด หรือย้อนหลัง |
| `ACCOUNT_PENDING` | 403 | Account ยังไม่ได้รับการอนุมัติ |
| `ACCOUNT_SUSPENDED` | 403 | Account ถูกระงับ |
| `DUPLICATE_EMAIL` | 409 | Email นี้มีในระบบแล้ว |
| `DUPLICATE_EMPLOYEE_CODE` | 409 | รหัสพนักงานนี้มีในระบบแล้ว |
| `CANNOT_CANCEL_BOOKING` | 400 | สถานะ booking ไม่สามารถยกเลิกได้ |

---

## 2. Auth Endpoints `/auth`

---

### `POST /auth/register` `[PUBLIC]`

สมัครสมาชิกใหม่

**Request Body:**
```json
{
  "email": "somchai@company.com",
  "password": "SecurePass123!",
  "employee_code": "EMP001",
  "full_name": "สมชาย ใจดี",
  "department": "IT",
  "phone": "0812345678"
}
```

**Validation:**
- `email` — format valid, unique
- `password` — min 8 chars, มีตัวเลขและตัวอักษร
- `employee_code` — unique, required
- `full_name` — required, max 255
- `department` — required

**Response `201`:**
```json
{
  "data": {
    "id": 1,
    "email": "somchai@company.com",
    "full_name": "สมชาย ใจดี",
    "status": "pending"
  },
  "message": "สมัครสมาชิกสำเร็จ กรุณารอการอนุมัติจาก Admin"
}
```

---

### `POST /auth/login` `[PUBLIC]`

เข้าสู่ระบบ

**Request Body:**
```json
{
  "email": "somchai@company.com",
  "password": "SecurePass123!"
}
```

**Response `200`:**
```json
{
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 28800,
    "user": {
      "id": 1,
      "email": "somchai@company.com",
      "full_name": "สมชาย ใจดี",
      "department": "IT",
      "role": "member",
      "status": "active"
    }
  }
}
```

**Error Cases:**
- `401` — email/password ไม่ถูกต้อง
- `403 ACCOUNT_PENDING` — ยังไม่ได้รับการอนุมัติ
- `403 ACCOUNT_SUSPENDED` — Account ถูกระงับ

---

### `GET /auth/me` `[AUTH]`

ดูข้อมูลผู้ใช้ปัจจุบัน

**Response `200`:**
```json
{
  "data": {
    "id": 1,
    "email": "somchai@company.com",
    "employee_code": "EMP001",
    "full_name": "สมชาย ใจดี",
    "department": "IT",
    "phone": "0812345678",
    "role": "member",
    "status": "active",
    "created_at": "2026-01-01T08:00:00"
  }
}
```

---

### `PUT /auth/me` `[AUTH]`

แก้ไขข้อมูลส่วนตัว (ไม่สามารถแก้ email และ employee_code)

**Request Body:**
```json
{
  "full_name": "สมชาย ใจดีมาก",
  "phone": "0898765432",
  "department": "DevOps"
}
```

**Response `200`:**
```json
{
  "data": { ...updated user object... },
  "message": "อัปเดตข้อมูลสำเร็จ"
}
```

---

## 3. Room Endpoints `/rooms`

---

### `GET /rooms` `[AUTH]`

ค้นหาห้องประชุมที่ว่าง

**Query Parameters:**

| Param | Type | Required | Description |
|---|---|---|---|
| `date` | `YYYY-MM-DD` | No | วันที่ต้องการจอง |
| `start_time` | `HH:MM` | No | เวลาเริ่มต้น |
| `end_time` | `HH:MM` | No | เวลาสิ้นสุด |
| `min_capacity` | integer | No | ความจุขั้นต่ำ |
| `building` | string | No | ชื่ออาคาร |
| `status` | string | No | เฉพาะ Admin: `active` / `inactive` / `all` |
| `page` | integer | No, default=1 | หน้า |
| `per_page` | integer | No, default=20 | จำนวนต่อหน้า |

**Response `200`:**
```json
{
  "data": [
    {
      "id": 1,
      "name": "ห้องประชุม A",
      "capacity": 10,
      "location": "อาคาร 1",
      "building": "อาคาร 1",
      "floor": "3",
      "description": "ห้องประชุมขนาดกลาง",
      "equipment": ["projector", "whiteboard"],
      "primary_image_url": "/uploads/rooms/1/primary.jpg",
      "is_available": true
    }
  ],
  "total": 5,
  "page": 1,
  "per_page": 20
}
```

**หมายเหตุ:** `is_available` = `true` เมื่อระบุ date + time และห้องว่างในช่วงนั้น

---

### `GET /rooms/{room_id}` `[AUTH]`

ดูรายละเอียดห้องพร้อม time slots ที่ถูกจองในวันที่ระบุ

**Query Parameters:**

| Param | Type | Required | Description |
|---|---|---|---|
| `date` | `YYYY-MM-DD` | No | วันที่ต้องการดู time slots |

**Response `200`:**
```json
{
  "data": {
    "id": 1,
    "name": "ห้องประชุม A",
    "capacity": 10,
    "location": "อาคาร 1",
    "building": "อาคาร 1",
    "floor": "3",
    "description": "ห้องประชุมขนาดกลาง",
    "equipment": ["projector", "whiteboard", "tv"],
    "images": [
      { "url": "/uploads/rooms/1/primary.jpg", "is_primary": true },
      { "url": "/uploads/rooms/1/side.jpg", "is_primary": false }
    ],
    "booked_slots": [
      {
        "start_time": "2026-05-07T09:00:00",
        "end_time": "2026-05-07T11:00:00",
        "status": "confirmed"
      }
    ]
  }
}
```

---

## 4. Booking Endpoints `/bookings`

---

### `POST /bookings` `[AUTH: member+]`

สร้างการจองใหม่

**Request Body:**
```json
{
  "room_id": 1,
  "title": "ประชุมทีม Q2 Planning",
  "description": "วางแผนงานไตรมาส 2",
  "start_time": "2026-05-10T09:00:00",
  "end_time": "2026-05-10T11:00:00",
  "attendee_count": 8
}
```

**Validation:**
- `start_time` ต้องเป็นอนาคต
- `end_time` > `start_time`
- `(end_time - start_time)` ≤ `max_booking_hours` จาก system_config
- วันที่จอง ≤ วันนี้ + `max_advance_days`
- จำนวน booking วันนั้น < `max_bookings_per_day`
- `attendee_count` ≤ room.capacity

**Response `201`:**
```json
{
  "data": {
    "id": 42,
    "room_id": 1,
    "title": "ประชุมทีม Q2 Planning",
    "start_time": "2026-05-10T09:00:00",
    "end_time": "2026-05-10T11:00:00",
    "attendee_count": 8,
    "status": "pending",
    "snap_room_name": "ห้องประชุม A",
    "snap_room_location": "อาคาร 1",
    "snap_user_name": "สมชาย ใจดี",
    "snap_user_department": "IT",
    "created_at": "2026-05-07T08:30:00"
  },
  "message": "จองห้องสำเร็จ กรุณารอการอนุมัติ"
}
```

**Error Cases:**
- `409 BOOKING_CONFLICT` — ห้องถูกจองซ้อนช่วงเวลานั้น
- `400 ROOM_INACTIVE` — ห้องถูกปิดการใช้งาน
- `400 BOOKING_RULE_VIOLATION` — ละเมิดกฎการจอง
- `400 INVALID_TIME_RANGE` — เวลาไม่ถูกต้อง

---

### `GET /bookings/me` `[AUTH]`

ดูรายการจองของตัวเอง

**Query Parameters:**

| Param | Type | Required | Description |
|---|---|---|---|
| `status` | string | No | filter: `pending`, `confirmed`, `rejected`, `cancelled` |
| `from_date` | `YYYY-MM-DD` | No | ตั้งแต่วันที่ |
| `to_date` | `YYYY-MM-DD` | No | ถึงวันที่ |
| `page` | integer | No, default=1 | — |
| `per_page` | integer | No, default=20 | — |

**Response `200`:**
```json
{
  "data": [
    {
      "id": 42,
      "title": "ประชุมทีม Q2 Planning",
      "snap_room_name": "ห้องประชุม A",
      "snap_room_location": "อาคาร 1",
      "start_time": "2026-05-10T09:00:00",
      "end_time": "2026-05-10T11:00:00",
      "attendee_count": 8,
      "status": "pending",
      "created_at": "2026-05-07T08:30:00",
      "approval": null
    }
  ],
  "total": 10,
  "page": 1,
  "per_page": 20
}
```

---

### `GET /bookings/{booking_id}` `[AUTH]`

ดูรายละเอียด booking (เฉพาะเจ้าของ หรือ Approver/Admin)

**Response `200`:**
```json
{
  "data": {
    "id": 42,
    "title": "ประชุมทีม Q2 Planning",
    "description": "วางแผนงานไตรมาส 2",
    "snap_room_name": "ห้องประชุม A",
    "snap_room_capacity": 10,
    "snap_room_location": "อาคาร 1",
    "snap_user_name": "สมชาย ใจดี",
    "snap_user_department": "IT",
    "snap_user_email": "somchai@company.com",
    "start_time": "2026-05-10T09:00:00",
    "end_time": "2026-05-10T11:00:00",
    "attendee_count": 8,
    "status": "confirmed",
    "created_at": "2026-05-07T08:30:00",
    "approval": {
      "approver_name": "วิภา รักงาน",
      "action": "approved",
      "reason": null,
      "actioned_at": "2026-05-07T09:00:00"
    }
  }
}
```

---

### `DELETE /bookings/{booking_id}` `[AUTH]`

ยกเลิกการจองของตัวเอง (status ต้องเป็น `pending` หรือ `confirmed`)

**Request Body:**
```json
{
  "reason": "ประชุมถูกยกเลิก"
}
```

**Response `200`:**
```json
{
  "data": { "id": 42, "status": "cancelled" },
  "message": "ยกเลิกการจองสำเร็จ"
}
```

---

### `GET /bookings/calendar` `[AUTH]`

ดูปฏิทินการจองภาพรวม (ทุกห้อง)

**Query Parameters:**

| Param | Type | Required | Description |
|---|---|---|---|
| `from_date` | `YYYY-MM-DD` | Yes | วันเริ่มต้น |
| `to_date` | `YYYY-MM-DD` | Yes | วันสิ้นสุด (max 31 วัน) |
| `room_id` | integer | No | filter เฉพาะห้อง |

**Response `200`:**
```json
{
  "data": [
    {
      "booking_id": 42,
      "room_id": 1,
      "room_name": "ห้องประชุม A",
      "title": "ประชุมทีม Q2 Planning",
      "start_time": "2026-05-10T09:00:00",
      "end_time": "2026-05-10T11:00:00",
      "status": "confirmed"
    }
  ]
}
```

---

## 5. Approval Endpoints `/approvals`

---

### `GET /approvals/pending` `[AUTH: approver+]`

ดูรายการจองที่รอการอนุมัติทั้งหมด

**Query Parameters:**

| Param | Type | Required | Description |
|---|---|---|---|
| `from_date` | `YYYY-MM-DD` | No | — |
| `to_date` | `YYYY-MM-DD` | No | — |
| `room_id` | integer | No | filter ตามห้อง |
| `page` | integer | No, default=1 | — |
| `per_page` | integer | No, default=20 | — |

**Response `200`:**
```json
{
  "data": [
    {
      "id": 42,
      "title": "ประชุมทีม Q2 Planning",
      "snap_room_name": "ห้องประชุม A",
      "snap_room_location": "อาคาร 1",
      "snap_user_name": "สมชาย ใจดี",
      "snap_user_department": "IT",
      "start_time": "2026-05-10T09:00:00",
      "end_time": "2026-05-10T11:00:00",
      "attendee_count": 8,
      "created_at": "2026-05-07T08:30:00"
    }
  ],
  "total": 3,
  "page": 1,
  "per_page": 20
}
```

---

### `POST /approvals/{booking_id}/approve` `[AUTH: approver+]`

อนุมัติการจอง

**Request Body:** *(ไม่มี body)*

**Response `200`:**
```json
{
  "data": {
    "booking_id": 42,
    "action": "approved",
    "actioned_at": "2026-05-07T09:00:00"
  },
  "message": "อนุมัติการจองสำเร็จ"
}
```

**Error Cases:**
- `404` — ไม่พบ booking
- `400` — booking ไม่ได้อยู่ในสถานะ `pending`
- `409 BOOKING_CONFLICT` — มี booking อื่น confirmed ซ้อนช่วงเวลาเดียวกันในขณะที่กำลัง approve

---

### `POST /approvals/{booking_id}/reject` `[AUTH: approver+]`

ปฏิเสธการจอง

**Request Body:**
```json
{
  "reason": "ห้องติดซ่อมบำรุงช่วงนั้น"
}
```

**Validation:** `reason` — required, min 10 chars

**Response `200`:**
```json
{
  "data": {
    "booking_id": 42,
    "action": "rejected",
    "reason": "ห้องติดซ่อมบำรุงช่วงนั้น",
    "actioned_at": "2026-05-07T09:00:00"
  },
  "message": "ปฏิเสธการจองสำเร็จ"
}
```

---

### `GET /approvals/history` `[AUTH: approver+]`

ดูประวัติการอนุมัติของตัวเอง

**Query Parameters:** `from_date`, `to_date`, `action` (`approved`/`rejected`), `page`, `per_page`

**Response `200`:**
```json
{
  "data": [
    {
      "booking_id": 42,
      "title": "ประชุมทีม Q2 Planning",
      "snap_user_name": "สมชาย ใจดี",
      "snap_room_name": "ห้องประชุม A",
      "start_time": "2026-05-10T09:00:00",
      "end_time": "2026-05-10T11:00:00",
      "action": "approved",
      "reason": null,
      "actioned_at": "2026-05-07T09:00:00"
    }
  ],
  "total": 25,
  "page": 1,
  "per_page": 20
}
```

---

## 6. Notification Endpoints `/notifications`

---

### `GET /notifications` `[AUTH]`

ดู notification ของตัวเอง

**Query Parameters:** `is_read` (boolean), `page`, `per_page`

**Response `200`:**
```json
{
  "data": [
    {
      "id": 10,
      "type": "booking_confirmed",
      "message": "การจองห้อง 'ห้องประชุม A' วันที่ 10 พ.ค. 09:00-11:00 ได้รับการอนุมัติแล้ว",
      "booking_id": 42,
      "is_read": false,
      "created_at": "2026-05-07T09:00:00"
    }
  ],
  "total": 5,
  "unread_count": 2,
  "page": 1,
  "per_page": 20
}
```

---

### `POST /notifications/{notification_id}/read` `[AUTH]`

ทำเครื่องหมายว่าอ่านแล้ว

**Response `200`:**
```json
{ "message": "แจ้งเตือนถูกทำเครื่องหมายว่าอ่านแล้ว" }
```

---

### `POST /notifications/read-all` `[AUTH]`

ทำเครื่องหมายอ่านทั้งหมด

**Response `200`:**
```json
{ "message": "แจ้งเตือน X รายการถูกทำเครื่องหมายว่าอ่านแล้ว" }
```

---

## 7. Admin Endpoints `/admin`

> ทุก endpoint ใน `/admin` ต้องมี `role = admin` เท่านั้น

---

### Member Management `/admin/users`

#### `GET /admin/users` `[AUTH: admin]`

ดูสมาชิกทั้งหมด

**Query Parameters:** `status`, `role`, `search` (ค้นตาม name/email/employee_code), `page`, `per_page`

**Response `200`:** paginated list ของ users

---

#### `GET /admin/users/pending` `[AUTH: admin]`

ดูสมาชิกที่รอการอนุมัติ

**Response `200`:** list ของ users ที่ `status = pending`

---

#### `POST /admin/users/{user_id}/approve` `[AUTH: admin]`

อนุมัติสมาชิก

**Response `200`:**
```json
{
  "data": { "id": 5, "status": "active" },
  "message": "อนุมัติสมาชิกสำเร็จ"
}
```

---

#### `POST /admin/users/{user_id}/reject` `[AUTH: admin]`

ปฏิเสธการสมัครสมาชิก

**Request Body:** `{ "reason": "..." }`

**Response `200`:**
```json
{
  "data": { "id": 5, "status": "rejected" },
  "message": "ปฏิเสธการสมัครสมาชิกสำเร็จ"
}
```

---

#### `POST /admin/users/{user_id}/suspend` `[AUTH: admin]`

ระงับ account

**Request Body:** `{ "reason": "..." }`

**Response `200`:** `{ "data": { "id": 5, "status": "suspended" } }`

---

#### `POST /admin/users/{user_id}/reactivate` `[AUTH: admin]`

เปิดใช้งาน account อีกครั้ง

**Response `200`:** `{ "data": { "id": 5, "status": "active" } }`

---

#### `PATCH /admin/users/{user_id}/role` `[AUTH: admin]`

เปลี่ยน role สมาชิก

**Request Body:**
```json
{ "role": "approver" }
```

**Response `200`:**
```json
{
  "data": { "id": 5, "role": "approver" },
  "message": "เปลี่ยน role สำเร็จ"
}
```

---

### Room Management `/admin/rooms`

#### `POST /admin/rooms` `[AUTH: admin]`

สร้างห้องใหม่

**Request Body:**
```json
{
  "name": "ห้องประชุม B",
  "capacity": 20,
  "location": "อาคาร 2 ชั้น 5",
  "building": "อาคาร 2",
  "floor": "5",
  "description": "ห้องประชุมขนาดใหญ่",
  "equipment": ["projector", "whiteboard", "microphone"]
}
```

**Validation:**
- `name` — unique within the same `building`
- `capacity` — positive integer

---

#### `PUT /admin/rooms/{room_id}` `[AUTH: admin]`

แก้ไขข้อมูลห้อง

**Request Body:** เหมือน POST (fields ที่ต้องการแก้ไข)

**Response `200`:** updated room object

---

#### `POST /admin/rooms/{room_id}/deactivate` `[AUTH: admin]`

ปิดการใช้งานห้อง

**Response `200`:** `{ "data": { "id": 1, "status": "inactive" } }`

---

#### `POST /admin/rooms/{room_id}/activate` `[AUTH: admin]`

เปิดการใช้งานห้อง

**Response `200`:** `{ "data": { "id": 1, "status": "active" } }`

---

#### `POST /admin/rooms/{room_id}/images` `[AUTH: admin]`

อัปโหลดรูปภาพห้อง

**Request:** `multipart/form-data`
- `file` — image file (jpg/png, max 5MB)
- `is_primary` — boolean

**Response `201`:**
```json
{
  "data": {
    "id": 3,
    "room_id": 1,
    "image_url": "/uploads/rooms/1/abc123.jpg",
    "is_primary": true
  }
}
```

---

### Booking Management `/admin/bookings`

#### `GET /admin/bookings` `[AUTH: admin]`

ดูการจองทั้งหมดในระบบ

**Query Parameters:** `status`, `room_id`, `user_id`, `from_date`, `to_date`, `page`, `per_page`

**Response `200`:** paginated list ของ bookings

---

#### `DELETE /admin/bookings/{booking_id}` `[AUTH: admin]`

ยกเลิกการจองใดก็ได้

**Request Body:** `{ "reason": "..." }` (required)

**Response `200`:** `{ "data": { "id": 42, "status": "cancelled" } }`

---

### System Configuration `/admin/configs`

#### `GET /admin/configs` `[AUTH: admin]`

ดูค่า config ทั้งหมด

**Response `200`:**
```json
{
  "data": [
    {
      "key": "max_advance_days",
      "value": "30",
      "description": "จองล่วงหน้าได้สูงสุด (วัน)"
    },
    {
      "key": "max_booking_hours",
      "value": "4",
      "description": "ระยะเวลาจองสูงสุดต่อครั้ง (ชั่วโมง)"
    },
    {
      "key": "max_bookings_per_day",
      "value": "3",
      "description": "จองได้สูงสุดต่อวัน (ครั้ง)"
    }
  ]
}
```

---

#### `PATCH /admin/configs/{key}` `[AUTH: admin]`

อัปเดตค่า config

**Request Body:**
```json
{ "value": "7" }
```

**Response `200`:**
```json
{
  "data": { "key": "max_advance_days", "value": "7" },
  "message": "อัปเดต config สำเร็จ"
}
```

---

### Dashboard `/admin/dashboard`

#### `GET /admin/dashboard` `[AUTH: admin]`

ข้อมูล Dashboard ภาพรวม

**Response `200`:**
```json
{
  "data": {
    "today": {
      "total_bookings": 12,
      "pending": 3,
      "confirmed": 8,
      "cancelled": 1
    },
    "pending_members": 2,
    "room_utilization": [
      { "room_id": 1, "room_name": "ห้องประชุม A", "utilization_percent": 75 },
      { "room_id": 2, "room_name": "ห้องประชุม B", "utilization_percent": 40 }
    ],
    "top_rooms_this_week": [
      { "room_id": 1, "room_name": "ห้องประชุม A", "booking_count": 18 }
    ],
    "bookings_this_week": [
      { "date": "2026-05-01", "count": 5 },
      { "date": "2026-05-02", "count": 8 }
    ]
  }
}
```

---

### Audit Log `/admin/audit-logs`

#### `GET /admin/audit-logs` `[AUTH: admin]`

ดู Audit Log

**Query Parameters:** `user_id`, `entity_type`, `action`, `from_date`, `to_date`, `page`, `per_page`

**Response `200`:**
```json
{
  "data": [
    {
      "id": 100,
      "user_id": 1,
      "user_name": "สมชาย ใจดี",
      "action": "booking.create",
      "entity_type": "booking",
      "entity_id": 42,
      "ip_address": "192.168.1.10",
      "created_at": "2026-05-07T08:30:00"
    }
  ],
  "total": 200,
  "page": 1,
  "per_page": 20
}
```

---

## 8. Health Check

### `GET /health` `[PUBLIC]`

**Response `200`:**
```json
{
  "status": "ok",
  "project": "P6BookingMe",
  "version": "0.1.0"
}
```

---

## 9. API Endpoints Summary

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | Public | สมัครสมาชิก |
| POST | `/auth/login` | Public | เข้าสู่ระบบ |
| GET | `/auth/me` | Auth | ดูโปรไฟล์ตัวเอง |
| PUT | `/auth/me` | Auth | แก้ไขโปรไฟล์ |
| GET | `/rooms` | Auth | ค้นหาห้อง |
| GET | `/rooms/{id}` | Auth | รายละเอียดห้อง |
| POST | `/bookings` | Auth | สร้างการจอง |
| GET | `/bookings/me` | Auth | รายการจองตัวเอง |
| GET | `/bookings/calendar` | Auth | ปฏิทินภาพรวม |
| GET | `/bookings/{id}` | Auth | รายละเอียดการจอง |
| DELETE | `/bookings/{id}` | Auth | ยกเลิกการจองตัวเอง |
| GET | `/approvals/pending` | Approver+ | รายการรออนุมัติ |
| POST | `/approvals/{id}/approve` | Approver+ | อนุมัติ |
| POST | `/approvals/{id}/reject` | Approver+ | ปฏิเสธ |
| GET | `/approvals/history` | Approver+ | ประวัติการอนุมัติ |
| GET | `/notifications` | Auth | ดู notifications |
| PATCH | `/notifications/{id}/read` | Auth | อ่านแล้ว |
| PATCH | `/notifications/read-all` | Auth | อ่านทั้งหมด |
| GET | `/admin/users` | Admin | จัดการสมาชิก |
| GET | `/admin/users/pending` | Admin | สมาชิกรออนุมัติ |
| POST | `/admin/users/{id}/approve` | Admin | อนุมัติสมาชิก |
| POST | `/admin/users/{id}/reject` | Admin | ปฏิเสธสมาชิก |
| POST | `/admin/users/{id}/suspend` | Admin | ระงับ account |
| POST | `/admin/users/{id}/reactivate` | Admin | เปิด account |
| PATCH | `/admin/users/{id}/role` | Admin | เปลี่ยน role |
| POST | `/admin/rooms` | Admin | สร้างห้อง |
| PUT | `/admin/rooms/{id}` | Admin | แก้ไขห้อง |
| POST | `/admin/rooms/{id}/deactivate` | Admin | ปิดห้อง |
| POST | `/admin/rooms/{id}/activate` | Admin | เปิดห้อง |
| POST | `/admin/rooms/{id}/images` | Admin | อัปโหลดรูป |
| GET | `/admin/bookings` | Admin | จองทั้งหมด |
| DELETE | `/admin/bookings/{id}` | Admin | ยกเลิกการจองใดก็ได้ |
| GET | `/admin/configs` | Admin | ดู config |
| PATCH | `/admin/configs/{key}` | Admin | แก้ไข config |
| GET | `/admin/dashboard` | Admin | Dashboard |
| GET | `/admin/audit-logs` | Admin | Audit logs |
| GET | `/health` | Public | Health check |
