# 09 — Security Design

---

## 1. Security Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Layer 1: Transport (HTTPS in production)           │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Layer 2: CORS Policy                               │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Layer 3: Authentication (JWT + DB status check)    │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Layer 4: Authorization (RBAC)                      │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Layer 5: Input Validation (Pydantic + Zod)         │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Layer 6: Data Security (bcrypt, no raw SQL)        │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Layer 7: Audit Trail (audit_logs table)            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Authentication — JWT Design

### 2.1 Token Structure

```python
# JWT Payload
{
  "sub": "1",                          # user_id (string)
  "email": "somchai@company.com",
  "role": "member",                    # member | approver | admin
  "iat": 1746604800,                   # issued at
  "exp": 1746633600                    # expires at (iat + 8 hours)
}
```

### 2.2 Token Lifecycle

```
POST /auth/login
    │
    ▼
ตรวจ email + bcrypt password
    │
    ▼
ตรวจ user.status == 'active'
    │
    ▼
สร้าง JWT ด้วย SECRET_KEY (HS256)
expire = now + 8 ชั่วโมง
    │
    ▼
ส่ง token กลับใน response body
    │
    ▼
Frontend เก็บใน Pinia authStore และ `localStorage` (หรือ `HttpOnly Cookie` ใน Phase 2)
เพื่อป้องกันปัญหาหลุดออกจากระบบเมื่อ Refresh หน้าจอ
    │
    ▼
ทุก request แนบ Header:
Authorization: Bearer <token>
    │
    ▼
Backend decode → ดึง user_id → query DB
ตรวจ user.status ทุกครั้ง → Suspend มีผลทันที
    │
    ▼
Token หมดอายุ → 401 → Frontend redirect /login
```

### 2.3 Implementation (Backend)

```python
# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict[str, Any]) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise InvalidTokenError()
```

### 2.4 Dependency Injection (Backend)

```python
# app/core/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import decode_access_token
from app.models.user import UserStatus, UserRole

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)          # ตรวจ signature + exp
    user_id: int = int(payload.get("sub"))

    user = await user_repo.get_by_id(db, user_id) # ← query DB ทุกครั้ง
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)

    if user.status == UserStatus.PENDING:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="ACCOUNT_PENDING")
    if user.status == UserStatus.SUSPENDED:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="ACCOUNT_SUSPENDED")
    if user.status == UserStatus.REJECTED:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="ACCOUNT_REJECTED")

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user  # status ผ่านแล้วจาก get_current_user

async def require_approver(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in (UserRole.APPROVER, UserRole.ADMIN):
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    return current_user

async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN)
    return current_user
```

### 2.5 Token Storage (Frontend)

```typescript
// stores/authStore.ts — เก็บใน localStorage และ memory เพื่อให้ Session ยังอยู่เมื่อ F5

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token') || null)
  const user = ref<CurrentUser | null>(null)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isApprover = computed(() =>
    user.value?.role === 'approver' || user.value?.role === 'admin'
  )
  const isAdmin = computed(() => user.value?.role === 'admin')

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }
})
```

```typescript
// services/axios.ts — แนบ token ทุก request

import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL })

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const auth = useAuthStore()
      auth.logout()                    // clear token
      window.location.href = '/login'  // redirect
    }
    return Promise.reject(err)
  }
)

export default api
```

---

## 3. Password Security

### 3.1 Policy

| กฎ | รายละเอียด |
|---|---|
| ความยาวขั้นต่ำ | 8 ตัวอักษร |
| ต้องมีตัวเลข | อย่างน้อย 1 ตัว |
| ต้องมีตัวอักษร | อย่างน้อย 1 ตัว |
| Algorithm | bcrypt (cost factor 12) |
| เก็บใน DB | hash เท่านั้น — ห้าม plain text ทุกกรณี |

### 3.2 Validation (Backend + Frontend)

```python
# app/schemas/auth.py (Pydantic)

import re
from pydantic import BaseModel, field_validator

class RegisterRequest(BaseModel):
    email: str
    password: str
    employee_code: str
    full_name: str
    department: str
    phone: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("รหัสผ่านต้องมีตัวอักษรอย่างน้อย 1 ตัว")
        if not re.search(r"\d", v):
            raise ValueError("รหัสผ่านต้องมีตัวเลขอย่างน้อย 1 ตัว")
        return v
```

```typescript
// types/schemas/auth.ts (Zod — Frontend)

import { z } from 'zod'

export const registerSchema = z.object({
  email: z.string().email('Email ไม่ถูกต้อง'),
  password: z
    .string()
    .min(8, 'รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร')
    .regex(/[A-Za-z]/, 'ต้องมีตัวอักษรอย่างน้อย 1 ตัว')
    .regex(/\d/, 'ต้องมีตัวเลขอย่างน้อย 1 ตัว'),
  employee_code: z.string().min(1, 'กรุณากรอกรหัสพนักงาน'),
  full_name: z.string().min(1, 'กรุณากรอกชื่อ-นามสกุล'),
  department: z.string().min(1, 'กรุณากรอกหน่วยงาน'),
  phone: z.string().optional(),
})
```

---

## 4. Authorization — RBAC

### 4.1 Role Hierarchy

```
admin
  └── inherits approver permissions
        └── inherits member permissions
```

### 4.2 Permission Matrix (Detailed)

| Resource / Action | member | approver | admin |
|---|:---:|:---:|:---:|
| **Auth** | | | |
| register, login | ✅ | ✅ | ✅ |
| view/edit own profile | ✅ | ✅ | ✅ |
| **Rooms** | | | |
| search rooms | ✅ | ✅ | ✅ |
| view room detail | ✅ | ✅ | ✅ |
| create/edit/deactivate room | ❌ | ❌ | ✅ |
| upload room images | ❌ | ❌ | ✅ |
| **Bookings** | | | |
| create booking | ✅ | ✅ | ✅ |
| view own bookings | ✅ | ✅ | ✅ |
| cancel own booking | ✅ | ✅ | ✅ |
| view all bookings | ❌ | ❌ | ✅ |
| cancel any booking | ❌ | ❌ | ✅ |
| view booking calendar | ✅ | ✅ | ✅ |
| **Approvals** | | | |
| view pending bookings | ❌ | ✅ | ✅ |
| approve booking | ❌ | ✅ | ✅ |
| reject booking | ❌ | ✅ | ✅ |
| view approval history | ❌ | ✅ | ✅ |
| **Notifications** | | | |
| view own notifications | ✅ | ✅ | ✅ |
| mark read | ✅ | ✅ | ✅ |
| **Admin — Users** | | | |
| view pending members | ❌ | ❌ | ✅ |
| approve/reject member | ❌ | ❌ | ✅ |
| suspend/reactivate account | ❌ | ❌ | ✅ |
| change user role | ❌ | ❌ | ✅ |
| **Admin — System** | | | |
| view/edit system configs | ❌ | ❌ | ✅ |
| view dashboard stats | ❌ | ❌ | ✅ |
| view audit logs | ❌ | ❌ | ✅ |

### 4.3 Resource Ownership Check

Member ต้องเข้าถึงได้เฉพาะ resource ของตัวเองเท่านั้น:

```python
# app/services/booking_service.py

async def cancel_booking(
    self,
    booking_id: int,
    current_user: User,
    reason: str,
) -> Booking:
    booking = await self.booking_repo.get_by_id(booking_id)
    if not booking:
        raise NotFoundException("ไม่พบการจอง")

    # Ownership check — member เข้าถึงได้เฉพาะของตัวเอง
    if current_user.role == UserRole.MEMBER:
        if booking.user_id != current_user.id:
            raise ForbiddenException("ไม่มีสิทธิ์ยกเลิกการจองนี้")

    # Admin ยกเลิกได้ทุก booking
    if booking.status not in (BookingStatus.PENDING, BookingStatus.CONFIRMED):
        raise BusinessRuleError("CANNOT_CANCEL_BOOKING")

    ...
```

---

## 5. CORS Policy

```python
# app/main.py

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,   # ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**ค่า ALLOWED_ORIGINS ตาม Environment:**

| Environment | ALLOWED_ORIGINS |
|---|---|
| Development | `["http://localhost:5173"]` |
| Production | `["https://your-domain.com"]` — ห้าม `"*"` |

**กฎเหล็ก:** ห้ามใช้ `allow_origins=["*"]` ในทุกกรณี

---

## 6. Input Validation

### 6.1 Validation Layers

```
Frontend (Zod + VeeValidate)
    │  ตรวจ client-side ก่อน submit — ลด round trip
    │
    ▼
Backend (Pydantic v2)
    │  ตรวจซ้ำเสมอ — ไม่ไว้วางใจ client
    │
    ▼
Database Constraints
    │  NOT NULL, UNIQUE, FK — last line of defense
```

### 6.2 Booking Input Validation (Backend)

```python
# app/schemas/booking.py

from pydantic import BaseModel, field_validator, model_validator
from datetime import datetime, timezone

class BookingCreate(BaseModel):
    room_id: int
    title: str
    description: str | None = None
    start_time: datetime
    end_time: datetime
    attendee_count: int

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("กรุณากรอกหัวข้อการประชุม")
        if len(v) > 255:
            raise ValueError("หัวข้อต้องไม่เกิน 255 ตัวอักษร")
        return v

    @field_validator("attendee_count")
    @classmethod
    def validate_attendee(cls, v: int) -> int:
        if v < 1:
            raise ValueError("จำนวนผู้เข้าร่วมต้องมากกว่า 0")
        return v

    @model_validator(mode="after")
    def validate_time_range(self) -> "BookingCreate":
        now = datetime.now(timezone.utc)
        if self.start_time <= now:
            raise ValueError("INVALID_TIME_RANGE: เวลาเริ่มต้นต้องเป็นอนาคต")
        if self.end_time <= self.start_time:
            raise ValueError("INVALID_TIME_RANGE: เวลาสิ้นสุดต้องมากกว่าเวลาเริ่มต้น")
        return self
```

### 6.3 SQL Injection Prevention

```python
# ✅ ถูกต้อง — SQLAlchemy ORM parameterized query
stmt = select(Booking).where(Booking.user_id == user_id)
result = await db.execute(stmt)

# ✅ ถูกต้อง — SQLAlchemy text() พร้อม bind params (กรณีจำเป็น)
stmt = text("SELECT * FROM bookings WHERE user_id = :uid").bindparams(uid=user_id)

# ❌ ผิด — ห้ามทำ string interpolation เด็ดขาด
stmt = text(f"SELECT * FROM bookings WHERE user_id = {user_id}")  # SQL Injection!
```

**กฎเหล็ก:** ใช้ SQLAlchemy ORM เสมอ — ไม่มี raw string SQL ในโค้ด

### 6.4 File Upload Security
API สำหรับอัปโหลดไฟล์ (เช่น ภาพห้องประชุม) ต้องมีการตรวจสอบอย่างเข้มงวด:
1. **MIME Type Validation**: ตรวจสอบ content จริงของไฟล์ (Magic Bytes) ผ่านไลบรารี เช่น `python-magic` ห้ามพิจารณาแค่ Extension (เช่น `.jpg`)
2. **File Size Limit**: จำกัดขนาดไฟล์ที่ระดับ Nginx และ FastAPI (เช่น สูงสุด 5MB)
3. **Filename Sanitization**: ห้ามใช้ชื่อไฟล์เดิมที่ผู้ใช้อัปโหลดมา ให้สุ่มชื่อใหม่ด้วย UUID เสมอ (เช่น `123e4567-e89b-12d3.jpg`) เพื่อป้องกัน Directory Traversal Attacks

---

## 7. Data Security

### 7.1 Sensitive Fields

| Field | การจัดการ |
|---|---|
| `password_hash` | bcrypt hash, **ห้าม** include ใน Response Schema เด็ดขาด |
| `email` | แสดงได้เฉพาะเจ้าของและ Admin |
| `employee_code` | แสดงได้เฉพาะเจ้าของและ Admin |
| `ip_address` | เก็บใน `audit_logs` เท่านั้น |

### 7.2 Response Schema กรอง Sensitive Fields

```python
# app/schemas/user.py

class UserResponse(BaseModel):
    id: int
    email: str
    employee_code: str
    full_name: str
    department: str
    role: UserRole
    status: UserStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
    # password_hash ไม่อยู่ใน schema → ไม่มีวันรั่วไหลใน response

class UserPublicResponse(BaseModel):
    """ใช้กับ Booking Approval list — แสดงแค่ชื่อ ไม่มี email"""
    id: int
    full_name: str
    department: str
    role: UserRole
```

### 7.3 Environment Variables

```bash
# .env — ห้าม commit ไฟล์นี้เด็ดขาด

SECRET_KEY=use-a-long-random-string-min-32-chars-here
DATABASE_URL=sqlite+aiosqlite:///./data/bookingme.db
ALLOWED_ORIGINS=["http://localhost:5173"]
```

```bash
# สร้าง SECRET_KEY ที่แข็งแกร่ง
python -c "import secrets; print(secrets.token_hex(32))"
```

**กฎ .gitignore:**
```
.env
*.env.*
!*.env.example
```

---

## 8. Audit Trail

ทุกการกระทำสำคัญต้องถูก log ใน `audit_logs` เสมอ เพื่อให้ตรวจสอบย้อนหลังได้:

```python
# app/services/audit_service.py

class AuditService:
    async def log(
        self,
        db: AsyncSession,
        user_id: int | None,
        action: str,
        entity_type: str,
        entity_id: int,
        old_value: dict | None = None,
        new_value: dict | None = None,
        ip_address: str | None = None,
    ) -> None:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
        )
        db.add(entry)
        # ไม่ commit แยก — ใช้ transaction เดียวกับ operation หลัก
```

**Actions ที่ต้อง Log:**

| Action String | เมื่อ |
|---|---|
| `user.register` | สมัครสมาชิก |
| `user.approve` | Admin อนุมัติสมาชิก |
| `user.reject` | Admin ปฏิเสธสมาชิก |
| `user.suspend` | Admin ระงับ account |
| `user.reactivate` | Admin เปิดใช้งาน account |
| `user.role_change` | Admin เปลี่ยน role |
| `booking.create` | Member สร้างการจอง |
| `booking.confirm` | Approver อนุมัติ |
| `booking.reject` | Approver ปฏิเสธ |
| `booking.cancel` | ยกเลิกการจอง |
| `room.create` | Admin สร้างห้อง |
| `room.update` | Admin แก้ไขห้อง |
| `room.deactivate` | Admin ปิดห้อง |
| `room.activate` | Admin เปิดห้อง |
| `config.update` | Admin แก้ไข config |

---

## 9. Security Checklist

### Backend
- [ ] `password_hash` ไม่อยู่ใน Response Schema ทุกตัว
- [ ] ทุก protected endpoint ใช้ `Depends(get_current_active_user)` หรือสูงกว่า
- [ ] ทุก Admin endpoint ใช้ `Depends(require_admin)`
- [ ] ทุก Approver endpoint ใช้ `Depends(require_approver)`
- [ ] Booking cancel ตรวจ ownership ก่อนเสมอ
- [ ] ไม่มี raw SQL string ใน codebase (ใช้ SQLAlchemy ORM)
- [ ] `SECRET_KEY` ไม่มีใน code หรือ git
- [ ] `ALLOWED_ORIGINS` ไม่ใช่ `"*"`
- [ ] ทุก audit action ถูก log ใน transaction เดียวกัน

### Frontend
- [ ] Token เก็บใน `localStorage` และ Pinia เพื่อแก้ปัญหา UX Session ขาดตอน
- [ ] Axios interceptor แนบ token ทุก request
- [ ] Axios interceptor redirect `/login` เมื่อ 401
- [ ] Navigation Guard ตรวจ role ก่อนเข้าแต่ละ route
- [ ] Zod validation ใน form ทุกตัวก่อน submit
- [ ] ไม่ render ปุ่ม/เมนูที่ user ไม่มีสิทธิ์ (v-if ตาม role)

### Environment
- [ ] `.env` อยู่ใน `.gitignore`
- [ ] มี `.env.example` เป็น template
- [ ] `SECRET_KEY` ยาวอย่างน้อย 32 chars (สร้างด้วย `secrets.token_hex(32)`)

---

## 10. Known Limitations (Phase 1)

| ข้อจำกัด | ผลกระทบ | แผนอนาคต |
|---|---|---|
| ไม่มี Rate Limiting | Brute force login ได้ | เพิ่ม slowapi หรือ nginx rate limit ใน Phase 2 |
| ไม่มี Refresh Token | Refresh หน้า = login ใหม่ | ยอมรับได้สำหรับ internal tool |
| JWT ไม่มี revocation list | Logout แล้ว token ยังใช้ได้จนหมดอายุ | DB status check ทุก request แก้ปัญหานี้แล้ว |
| ไม่มี 2FA | — | Phase 3 (ถ้าจำเป็น) |
| HTTP ใน dev | ไม่เป็นไร สำหรับ localhost | HTTPS บังคับใน production |
