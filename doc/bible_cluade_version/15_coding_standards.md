# 15 — Coding Standards and Conventions

---

## 1. Overview

เอกสารฉบับนี้กำหนดมาตรฐานการเขียนโค้ด (Coding Standards) และข้อตกลงร่วมกัน (Conventions) สำหรับทีมพัฒนา P6BookingMe เพื่อให้โค้ดมีคุณภาพ อ่านง่าย บำรุงรักษาง่าย และเป็นไปในทิศทางเดียวกันทั้งโปรเจกต์

---

## 2. Git Workflow & Commit Messages

### 2.1 Branching Strategy (Trunk-based Development)
- **`main`**: โค้ดที่พร้อมสำหรับการ Deploy ขึ้น Production (เสถียรที่สุด)
- **`feature/<name>`**: สำหรับการพัฒนาฟีเจอร์ใหม่ (เช่น `feature/user-auth`, `feature/room-crud`)
- **`bugfix/<name>`**: สำหรับการแก้ไขบัค (เช่น `bugfix/conflict-check-error`)
- **`hotfix/<name>`**: สำหรับแก้ไขบัคฉุกเฉินบน Production ทันที

### 2.2 Commit Message Format (Conventional Commits)
รูปแบบ: `<type>(<scope>): <subject>`

**Types ที่อนุญาต:**
- `feat`: เพิ่มฟีเจอร์ใหม่
- `fix`: แก้ไขบัค
- `docs`: อัปเดตเอกสาร (เช่น README, ไฟล์ใน `doc/`)
- `style`: จัดฟอร์แมตโค้ด, ลบ space ว่าง (ไม่กระทบ logic)
- `refactor`: ปรับปรุงโค้ดโดยไม่เพิ่มฟีเจอร์หรือแก้บัค
- `test`: เพิ่มหรือแก้ไข Unit/E2E test
- `chore`: อัปเดตเครื่องมือ, config, dependencies

**ตัวอย่าง:**
- `feat(auth): implement JWT login endpoint`
- `fix(booking): resolve overlap checking logic`
- `docs(api): update swagger descriptions for rooms`

---

## 3. Backend Conventions (Python / FastAPI)

### 3.1 Naming Conventions
- **Variables / Functions:** ใช้ `snake_case` (เช่น `get_user_by_id`, `is_active`)
- **Classes:** ใช้ `PascalCase` (เช่น `UserRepository`, `BookingCreate`)
- **Constants:** ใช้ `UPPER_SNAKE_CASE` (เช่น `MAX_ADVANCE_DAYS`, `JWT_SECRET`)
- **Private Variables:** นำหน้าด้วย `_` (เช่น `_db_session`, `_hash_password()`)

### 3.2 Code Formatting & Linting
- บังคับใช้ **Black** สำหรับ Code Formatting (Line length = 88)
- บังคับใช้ **isort** สำหรับการเรียง Imports (Standard Library -> Third-party -> Local Code)
- แนะนำให้ใช้ **Flake8** หรือ **Ruff** ในการทำ Linting เพื่อตรวจสอบ Syntax และ Code Smells

### 3.3 Type Hinting
- **ต้องใส่ Type Hints เสมอ** ทั้งพารามิเตอร์ขาเข้าและผลลัพธ์ (Return Type) ของฟังก์ชัน
- ช่วยให้ IDE (เช่น VSCode) สามารถทำ Auto-complete ได้ถูกต้อง และลดบัคระหว่างพัฒนา
```python
# ❌ ผิด (ไม่มี Type Hints)
def calculate_duration(start, end):
    pass

# ✅ ถูกต้อง
from datetime import datetime

def calculate_duration(start: datetime, end: datetime) -> int:
    pass
```

### 3.4 Performance & Query Optimization
- **ป้องกัน N+1 Query Problem:** ห้ามใช้ Lazy Loading แบบวนลูปดึงข้อมูล (เช่น การเข้าถึง `booking.user` ภายในลูป `for booking in bookings`) ให้ใช้ **`selectinload`** หรือ **`joinedload`** เสมอใน Query เมื่อต้องการดึงข้อมูลที่มีความสัมพันธ์ (Relationships) มาใช้งาน

---

## 4. Frontend Conventions (Vue 3 / TypeScript)

### 4.1 Vue Component Structure (SFC - Single File Component)
จัดเรียงลำดับบล็อกในไฟล์ `.vue` เสมอ เพื่อให้อ่านง่าย:
1. `<script setup lang="ts">` (ลอจิก)
2. `<template>` (โครงสร้าง UI)
3. `<style scoped>` (สไตล์เฉพาะ Component)

### 4.2 Naming Conventions
- **Component Files:** ใช้ `PascalCase` (เช่น `RoomCard.vue`, `UserList.vue`)
- **Composables:** นำหน้าด้วย `use` และเป็น `camelCase` (เช่น `useAuth.ts`, `useBookingForm.ts`)
- **Views/Pages:** ลงท้ายด้วยคำว่า `Page` เสมอ (เช่น `LoginPage.vue`, `DashboardPage.vue`)
- **Stores (Pinia):** ใช้ `camelCase` (เช่น `authStore.ts`, `roomStore.ts`)

### 4.3 State Management Rules
- ไม่ควรแก้ไข State ใน Pinia จาก Component โดยตรง (หลีกเลี่ยง `authStore.user = null`)
- **ต้องเรียกผ่าน Action เสมอ** (เช่น `authStore.logout()`) เพื่อให้ง่ายต่อการ Debug และมี Logic ส่วนกลาง

### 4.4 CSS & Styling (TailwindCSS)
- ใช้ Tailwind Utility Classes ใน `<template>` เป็นหลัก
- หาก Class เริ่มยาวหรือมีการใช้ซ้ำบ่อย ให้แยกเป็น Component หรือนำไปประกาศใน `@apply` ภายใน `<style scoped>`
- ไม่เขียน CSS ปกติผสม (เช่น `margin-top: 10px;`) ถ้าไม่จำเป็นจริงๆ

---

## 5. API Design & RESTful Rules

- **Nouns, Not Verbs:** ใช้คำนามในการตั้งชื่อ Endpoint (เช่น `GET /bookings` ไม่ใช่ `GET /get-bookings`)
- **Plural Nouns:** ใช้คำนามพหูพจน์เสมอ (เช่น `/users`, `/rooms`)
- **Nesting:** ถ้ามีความสัมพันธ์กันให้ซ้อน Path (เช่น `GET /rooms/1/images`)
- **Pagination:** Response ที่เป็น List หรือ Array ควรมี Pagination เสมอ (เว้นแต่รู้แน่ชัดว่าข้อมูลน้อยมาก)
- **Idempotency (การป้องกันข้อมูลซ้ำ):** สำหรับ API ที่สร้างหรือเปลี่ยนแปลงข้อมูล (POST/PUT/DELETE) ฝั่ง Frontend ต้องทำการ Debounce (ปิดปุ่มกด) ป้องกันปัญหากดเบิ้ล (Double-click) และฝั่ง Backend ควรออกแบบเผื่อการรันคำสั่งซ้ำซ้อนอย่างปลอดภัย (เช่น การใช้ `SELECT FOR UPDATE` แบบที่ออกแบบไว้)

---

## 6. Testing Conventions

- **Unit Tests (`pytest` / `vitest`):**
  - ชื่อไฟล์ต้องขึ้นต้นด้วย `test_` (เช่น `test_booking_service.py`)
  - ชื่อฟังก์ชัน Test ต้องอธิบาย Case ชัดเจน (เช่น `test_create_booking_fails_when_room_inactive`)
  - ใช้หลักการ **Arrange-Act-Assert (AAA)** ในทุกๆ Test
- **E2E Tests (Playwright):**
  - เน้นเทสเฉพาะ "Critical Path" เช่น การ Login, การสร้างและอนุมัติการจอง
  - ไม่ควรใช้ E2E เทสสิ่งเล็กๆ น้อยๆ ที่ Unit Test ทำได้ (เพราะช้ากว่าและใช้ทรัพยากรสูงกว่า)

---

## 7. Database & Migrations Rules

### 7.1 Zero-Downtime Migration Pattern
- **ห้ามแก้ไข (Rename/Drop) คอลัมน์โดยตรง:** ในการทำ Database Migration ด้วย Alembic ห้ามใช้คำสั่ง `DROP COLUMN` หรือ `ALTER TABLE RENAME` กับตารางที่รันอยู่บน Production ในขั้นตอนเดียว เพราะจะทำให้แอปพลิเคชันพัง (Downtime)
- **ให้ใช้รูปแบบ Expand and Contract:**
  1. *Expand:* สร้างคอลัมน์ใหม่ขึ้นมาตีคู่กัน
  2. *Migrate Data:* ทยอยคัดลอกข้อมูลจากคอลัมน์เก่าไปใหม่ (และให้แอปฯ อ่าน/เขียนลงทั้งคู่)
  3. *Contract:* อัปเดตแอปให้ใช้คอลัมน์ใหม่ 100% แล้วค่อยปล่อย Migration ตัวใหม่มาลบคอลัมน์เก่าทิ้ง
