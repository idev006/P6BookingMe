# 10 — Architecture Decision Records (ADR)

> บันทึกการตัดสินใจสถาปัตยกรรมที่สำคัญ พร้อมเหตุผลและทางเลือกที่พิจารณา

---

## ADR-001 — Monolithic Architecture (ไม่ใช้ Microservices)

**Status:** Accepted  
**Date:** 2026-05

### Context
ระบบ P6BookingMe เป็น internal tool สำหรับองค์กรขนาดเล็ก-กลาง ใช้งานภายใน

### Decision
ใช้ **Monolith** — FastAPI app เดียว, Vue frontend เดียว

### Rationale
- ทีมพัฒนาขนาดเล็ก deployment และ debugging ง่ายกว่า
- ปริมาณ traffic ไม่สูง ไม่จำเป็นต้อง scale แยกส่วน
- Microservices เพิ่ม complexity (service discovery, distributed tracing, network latency)

### Consequences
- Scale ทั้ง app พร้อมกัน ไม่สามารถ scale เฉพาะส่วน
- หากโตขึ้นมากอาจต้อง refactor — แต่ Strict Layering ช่วยให้ migrate ได้ในอนาคต

---

## ADR-002 — Strict Layer Architecture (API → Service → Repository)

**Status:** Accepted  
**Date:** 2026-05

### Context
ต้องการโครงสร้างที่ testable, maintainable และไม่ผสม business logic กับ database logic

### Decision
บังคับ 3 layers:
1. **API Layer** — รับ request, validate input, return response
2. **Service Layer** — business logic, orchestration
3. **Repository Layer** — database queries only

### Rationale
- API layer ไม่ควรรู้จัก SQLAlchemy
- Service layer ไม่ควรรู้จัก HTTP request/response
- Repository layer ไม่ควรมี business rules

### Consequences
- Code เยอะกว่า flat structure
- ทดสอบแต่ละ layer แยกกันได้ง่าย
- เปลี่ยน ORM หรือ database โดยแก้เฉพาะ repository layer

---

## ADR-003 — SQLite (dev) → ยืดหยุ่นไปยัง MySQL/PostgreSQL (prod)

**Status:** Accepted  
**Date:** 2026-05

### Context
ต้องการ dev environment ที่ setup ง่าย แต่ production ต้องรองรับ multi-user concurrent writes

### Decision
ใช้ **SQLAlchemy async ORM** กับ `DATABASE_URL` ใน `.env`
- Dev: `sqlite+aiosqlite:///./data/bookingme.db`
- Prod: `mysql+aiomysql://...` หรือ `postgresql+asyncpg://...`

### Rationale
- SQLAlchemy abstraction ทำให้เปลี่ยน driver โดยไม่แก้ logic
- ไม่เขียน raw SQL ยกเว้น performance-critical queries
- Alembic migration รองรับ multiple dialects

### Consequences
- **`SELECT FOR UPDATE`** ใช้งานไม่ได้กับ SQLite — ใช้ transaction isolation แทนในช่วง dev
- ต้อง test conflict prevention บน real database ใน CI

---

## ADR-004 — JWT Stateless + DB Status Check

**Status:** Accepted  
**Date:** 2026-05

### Context
JWT แบบ pure stateless ไม่สามารถ revoke token ได้ก่อนหมดอายุ — เป็นช่องโหว่เมื่อ admin ต้องการ suspend user

### Decision
ทุก protected request ต้อง:
1. ตรวจ JWT signature + expiry
2. **Query DB** ตรวจ `user.status == active`

### Rationale
- User ถูก suspend → request ถัดไปล้มเหลวทันที แม้ token ยังไม่หมดอายุ
- ไม่ต้องใช้ token blacklist (Redis) ซึ่งเพิ่ม infrastructure
- DB query มีต้นทุน แต่ยอมรับได้เพราะ user table เล็กและ indexed by id

### Consequences
- ทุก API call มี DB query เพิ่ม 1 ครั้ง
- ถ้า DB down → API ทุก endpoint ล้มเหลว (acceptable — ระบบ internal)
- Token expiry: 8 ชั่วโมง (ลดจำนวน DB hits เทียบกับ short-lived token)

---

## ADR-005 — Booking Snapshot Pattern

**Status:** Accepted  
**Date:** 2026-05

### Context
ข้อมูลห้อง (ชื่อ, ความจุ) อาจเปลี่ยนแปลงได้ แต่การจองที่ผ่านมาควรแสดงข้อมูล ณ เวลาที่จอง

### Decision
เมื่อสร้าง Booking ให้ **copy ข้อมูล Room** ลงใน booking record:
- `room_name_snapshot`
- `room_capacity_snapshot`
- `room_location_snapshot`

### Rationale
- ประวัติการจองถูกต้องแม้ room ถูกแก้ไขหรือลบในภายหลัง
- Audit trail ครบถ้วน
- ไม่ต้อง JOIN หลาย table เพื่อแสดงประวัติ

### Consequences
- ข้อมูล Room เปลี่ยน ไม่กระทบ booking ที่ confirmed แล้ว
- Storage เพิ่มขึ้นเล็กน้อย (acceptable)

---

## ADR-006 — Conflict Prevention ด้วย SELECT FOR UPDATE

**Status:** Accepted  
**Date:** 2026-05

### Context
Double-booking: สองคน book ห้องเดียวกัน เวลาเดียวกัน พร้อมกัน

### Decision
ใช้ **`SELECT FOR UPDATE`** lock row ก่อน conflict check ใน production database

```python
# ใน BookingService.create_booking()
async with session.begin():
    await session.execute(
        select(Booking)
        .where(Booking.room_id == room_id)
        .where(Booking.status.in_(["confirmed", "pending"]))
        .with_for_update()
    )
    # ตรวจ overlap
    # ถ้าไม่ conflict → create booking
```

### Rationale
- Application-level check ไม่เพียงพอ (race condition)
- `UNIQUE` constraint ทำ conflict check ยาก (start/end time overlap)
- `SELECT FOR UPDATE` ป้องกัน concurrent writes ในช่วงเวลาเดียวกัน

### Consequences
- SQLite dev ไม่รองรับ `FOR UPDATE` — ใช้ serializable transaction แทน
- ต้อง test ใน MySQL/PostgreSQL ก่อน production

---

## ADR-007 — Registration ต้องผ่าน Admin อนุมัติ

**Status:** Accepted  
**Date:** 2026-05

### Context
ระบบเป็น internal — ไม่ควรให้ใครก็ได้สมัครสมาชิกแล้วใช้งานได้ทันที

### Decision
- User ที่ register มี status = `pending`
- ต้องรอ Admin เปลี่ยน status เป็น `active` ก่อนจึง login ได้

### Rationale
- ควบคุม access ระดับ organization
- ป้องกัน unauthorized access
- Admin เห็น list ของ pending users และสามารถ approve/reject

### Consequences
- User experience: รอการอนุมัติก่อน login ได้
- Admin ต้องทำ onboarding ทุก user ใหม่
- ต้องมี notification ให้ Admin รู้เมื่อมี pending user ใหม่

---

## ADR-008 — Vue 3 Composition API + `<script setup>` only

**Status:** Accepted  
**Date:** 2026-05

### Context
Vue 3 รองรับทั้ง Options API และ Composition API

### Decision
ใช้ **Composition API + `<script setup lang="ts">`** เท่านั้น ห้ามใช้ Options API

### Rationale
- Better TypeScript inference
- Logic reuse ผ่าน Composables (ไม่ต้องใช้ Mixins)
- Vue 3 ecosystem (Pinia, VueUse) ออกแบบมาสำหรับ Composition API

### Consequences
- ต้องเรียนรู้ `ref()`, `computed()`, `watch()` pattern
- Code อ่านง่ายขึ้นเมื่อเคยชิน
- Options API code จะถูก reject ใน code review

---

## ADR-009 — TailwindCSS v4 + DaisyUI v5

**Status:** Accepted  
**Date:** 2026-05

### Context
ต้องการ UI component library ที่ integrate กับ Tailwind และ Vue ได้ง่าย

### Decision
- **TailwindCSS v4** + **@tailwindcss/vite** plugin (ไม่ใช้ PostCSS config แบบเก่า)
- **DaisyUI v5** สำหรับ pre-built components

### Rationale
- TailwindCSS v4 ใช้ Vite plugin โดยตรง — config น้อยกว่า
- DaisyUI v5 compatible กับ Tailwind v4
- Semantic class names (btn, card, modal) อ่านง่าย
- ปรับ theme ผ่าน CSS variables

### Consequences
- TailwindCSS v4 ยังค่อนข้างใหม่ — breaking changes จาก v3 บางส่วน
- ต้อง check DaisyUI v5 component names (บางตัวเปลี่ยนจาก v4)

---

## ADR-010 — JWT Token Storage Strategy (ปรับปรุงตาม Audit Recommendation)

**Status:** Accepted (Revised)  
**Date:** 2026-05

### Context
JWT token ต้องเก็บที่ไหนสักที่ฝั่ง Frontend 

### Decision
- **Phase 1:** เก็บ Token ใน `localStorage` + Pinia Store ไปก่อน
- **Phase 2 (Future):** อัปเกรดเป็น **HttpOnly Secure Cookie**

### Rationale
- UX สำคัญ: การเก็บใน Memory ทำให้ Refresh หน้าแล้วหลุด (Pain point ที่เจอบ่อยสุด)
- Vue 3 มีการป้องกัน XSS ให้อัตโนมัติ (ผ่าน template escaping) จึงลดความเสี่ยงของการเก็บใน `localStorage` ได้
- HttpOnly Cookie ดีที่สุด แต่ซับซ้อนสำหรับ MVP 

### Consequences
- ผู้ใช้ไม่ต้องล็อกอินใหม่ทุกครั้งที่กด F5
- ต้องระวังห้ามใช้ `v-html` หรือ library ที่ทำ DOM Injection เสี่ยงต่อ XSS payload 

---

## ADR-011 — Docker Multi-stage Build สำหรับ Frontend

**Status:** Accepted  
**Date:** 2026-05

### Context
Frontend build artifacts (dist/) เล็กกว่า node_modules มาก — ไม่ควร ship node_modules เข้า container

### Decision
ใช้ **multi-stage Docker build**:
- Stage 1: `node:20-alpine` — `npm ci && npm run build`
- Stage 2: `nginx:alpine` — copy `dist/` เท่านั้น

### Rationale
- Image size ลดจาก ~500MB (node) เหลือ ~25MB (nginx + dist)
- Production container ไม่มี build tools หรือ dev dependencies
- Security surface ลดลง

### Consequences
- Build time นานกว่า single-stage
- Nginx config ต้องมี SPA fallback (`try_files $uri /index.html`)
- API proxy ผ่าน nginx ไปยัง backend container

---

## Summary Table

| ADR | Decision | Status |
|-----|----------|--------|
| 001 | Monolithic Architecture | Accepted |
| 002 | Strict Layer (API→Service→Repository) | Accepted |
| 003 | SQLite dev / ORM for flexibility | Accepted |
| 004 | JWT + DB status check | Accepted |
| 005 | Booking Snapshot Pattern | Accepted |
| 006 | SELECT FOR UPDATE conflict prevention | Accepted |
| 007 | Registration requires Admin approval | Accepted |
| 008 | Vue 3 Composition API only | Accepted |
| 009 | TailwindCSS v4 + DaisyUI v5 | Accepted |
| 010 | LocalStorage JWT (Phase 1) → HttpOnly Cookie (Phase 2) | Accepted (Revised) |
| 011 | Docker multi-stage frontend build | Accepted |
| 012 | Caching User Status with Redis | Planned (Future) |

---

## ADR-012 — Caching User Status (Future Phase Recommendation)

**Status:** Planned (Future)  
**Date:** 2026-05

### Context
การให้ `get_current_user` ไป Query DB ทุึกๆ Request เพื่อตรวจสอบ Status (`active`/`suspended`) ทำให้ Database รับภาระหนัก

### Decision
ใช้ Redis ทำ Session Caching ในอนาคต เมื่อปริมาณผู้ใช้งานเพิ่มสูงขึ้น

### Rationale
- ลดจำนวน Database Hits ได้มากกว่า 90% ของ Traffic 
- เมื่อ Admin แก้ไขสถานะ User ค่อยให้ไปลบ/อัปเดต Cache ใน Redis 

### Consequences
- ต้องเพิ่มโครงสร้างพื้นฐาน (Redis Container) 
- มีความซับซ้อนเรื่อง Cache Invalidation (รอขึ้นใน Phase 2 หรือ Phase 3)
