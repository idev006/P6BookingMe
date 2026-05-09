# Sprint 5.4 — Reporting & Analytics Export 🚀

> ส่วนงานเก็บตกเพื่อให้ครบถ้วนตาม Bible (FR-09 และ UC-CAL-05) และเสริมความแข็งแกร่งด้าน Business Rules

### 📋 Tasks:

#### 1. Backend: Analytics & Statistics
- [x] API: `GET /api/v1/admin/reporting/summary` (วันนี้จองเท่าไหร่, รออนุมัติเท่าไหร่)
- [x] API: `GET /api/v1/admin/reporting/frequent-rooms` (ห้องที่ถูกจองมากที่สุด 5 อันดับ)
- [x] API: `GET /api/v1/admin/reporting/usage-trends` (แนวโน้มการใช้งานรายวัน/รายสัปดาห์)

#### 2. Backend: Data Export (UC-CAL-05)
- [x] Service: CSV/Excel Export Utility
- [x] API: `GET /api/v1/admin/reporting/export/bookings` (Export รายการจองตามช่วงเวลาและสถานะ)
- [x] Feature: "Maid View" Export (รายการจองสำหรับแม่บ้านเพื่อเตรียมห้อง)

#### 3. Frontend: Admin Insights UI
- [x] UI: Analytics Cards (สรุปตัวเลขสำคัญบน Dashboard)
- [x] UI: Simple Charts (ใช้ไลบรารีขนาดเล็กเพื่อแสดงเทรนด์การใช้งาน)
- [x] UI: Export Action Buttons (ปุ่มดาวน์โหลดในหน้า All Bookings และ Calendar)

#### 4. Business Rules Reinforcement (Bible Compliance)
- [x] Logic: ตรวจสอบ BR-02 (จำกัดการจอง N ครั้งต่อวัน) ใน `BookingService`
- [x] Logic: ตรวจสอบ BR-04 (จำกัดระยะเวลาจองสูงสุด N ชั่วโมง) ใน `BookingService`

---

### 🛡️ Audit & Verification:
- [ ] Unit Test สำหรับ BR-02/04 Enforcement
- [ ] Verification: ตรวจสอบไฟล์ Export ว่าข้อมูลถูกต้องตาม Snapshot Logic
