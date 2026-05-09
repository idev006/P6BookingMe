# Sprint 6.3 — Member UX Enhancement

## Objective
ยกระดับประสบการณ์การใช้งานของผู้ใช้กลุ่ม Member ให้มีความยืดหยุ่นและเป็นมืออาชีพมากขึ้น โดยมุ่งเน้นไปที่การจัดการรายการจองที่เคยทำไว้ (Edit & Duplicate) ตามมาตรฐาน World Class UI/UX

> [ดูผังการทำงาน (Sequence Diagrams) ทั้งหมด ได้ที่นี่ (Booking, Edit, Duplicate, Cancel, Approve, Reject)](./sequence_diagrams.md)

---

## 🛠 Features Implemented

### 1. Edit Booking (แก้ไขการจอง)
- **Backend**: 
    - เพิ่ม Endpoint `PATCH /api/v1/bookings/{id}`
    - พัฒนา Logic การ Reset สถานะ: หากมีการแก้ไขรายการที่อนุมัติแล้ว (`CONFIRMED`) ระบบจะเปลี่ยนสถานะกลับเป็น `PENDING` โดยอัตโนมัติ
- **Frontend**:
    - เพิ่มปุ่มแก้ไขในหน้า Dashboard และ Detail Modal
    - พัฒนาโหมดการทำงานพิเศษในหน้า `BookingPage.vue` ให้รองรับการ "Update" แทนการ "Create"

### 2. Quick Re-book / Duplicate (จองซ้ำด่วน)
- **Logic**: ช่วยให้ผู้ใช้สามารถคัดลอกข้อมูลจากการจองเดิมมาเป็นต้นแบบสำหรับการจองครั้งใหม่ได้ทันที
- **UI**: เพิ่มปุ่มไอคอนคัดลอกในตารางรายการจอง ช่วยลดขั้นตอนการกรอกข้อมูลซ้ำ

### 3. Dashboard UX Enhancement (Search & Filter)
- **Search**: พัฒนาระบบค้นหาแบบ Real-time ตามหัวข้อประชุมหรือชื่อห้อง
- **Filtering**: เพิ่มระบบ Tab Filter กรองสถานะการจอง (Pending, Confirmed, Rejected)
- **Empty States**: ออกแบบหน้าจอกรณีไม่พบข้อมูลให้มีความเป็นมืออาชีพ (Premium Look) และมีปุ่ม Action ที่ชัดเจน

### 4. Server-Side DataTable Migration (การโอนย้ายระบบจัดการตารางสู่ Server-side)
- **Objective**: เปลี่ยนการค้นหา (Search), การกรอง (Filter) และการแบ่งหน้า (Pagination) จากฝั่ง Client มาประมวลผลที่ Database ทั้งหมด เพื่อรองรับข้อมูลขนาดใหญ่
- **Standardization**:
    - ทุกตารางหลักใช้มาตรฐาน **ROWS per page** เดียวกัน (5, 10, 15, 25, 50)
    - ระบบ **Debounced Search** (500ms) ลดการเรียก API ถี่เกินไป
    - แสดงผล **Showing X-Y of Z** ที่ถูกต้องตามข้อมูลจริงในฐานข้อมูล
- **Components Migrated**:
    - `Dashboard.vue` (Member Recent Bookings)
    - `AllBookings.vue` (Admin All Bookings)
    - `UserManagement.vue` (Admin Users)
    - `AuditLogs.vue` (Admin Audit)
    - `RoomManagement.vue` (Admin Rooms)
    - `PendingApprovals.vue` (Admin Approvals)

---

## 🎨 UI/UX Standardization
- **Center Middle Alignment**: ตรวจสอบและปรับปรุงการจัดวางตัวอักษรและไอคอนให้กึ่งกลางเป๊ะ
*   **World-Class DataTable Pattern**:
    *   **Real-time Search**: Integrated multi-field search for instant data retrieval.
    *   **Status Filtering**: Advanced dropdown filters for complex datasets (e.g., Booking Status, User Role).
    *   **Configurable Page Size**: Standardized selector (5, 10, 15, 25, 50) with solid background to prevent visibility issues.
    *   **Professional Pagination**: Consistent header/footer layout with descriptive counters.
    *   **Premium Aesthetic**: Utilization of `font-black`, `uppercase`, and `tracking-widest`.
- **Global Alignment**: All components across Member and Admin modules now strictly follow this design system.

---

## 📝 Files Impacted

### Backend:
- `app/repositories/booking.py` (Added multi-field ILIKE search)
- `app/services/booking.py` (Updated to handle search/filter params)
- `app/api/v1/endpoints/bookings.py` (Member endpoint migration)
- `app/api/v1/endpoints/admin_bookings.py` (Admin endpoint migration)
- `app/api/v1/endpoints/admin_users.py`
- `app/api/v1/endpoints/admin_audit.py`
- `app/api/v1/endpoints/approvals.py`

### Frontend:
- `src/services/booking.ts` & `src/services/audit.ts` & `src/services/approval.ts`
- `src/stores/booking.ts` & `src/stores/room.ts` & `src/stores/approval.ts`
- `src/views/Dashboard.vue`
- `src/views/admin/AllBookings.vue`
- `src/views/admin/UserManagement.vue`
- `src/views/admin/AuditLogs.vue`
- `src/views/admin/RoomManagement.vue`
- `src/views/admin/PendingApprovals.vue`

---

## ✅ Status: COMPLETED (Enterprise Grade)
ฟีเจอร์การจัดการรายการจองและการประมวลผลข้อมูลระดับองค์กร (Server-side) ได้รับการติดตั้งและทดสอบอย่างสมบูรณ์แบบ มั่นใจในประสิทธิภาพและความลื่นไหลแม้มีข้อมูลจำนวนมาก
