# Sprint 3.1 — Booking Models & CRUD (Backend) 🏃

> พัฒนาฐานข้อมูลและ API พื้นฐานสำหรับการจองห้องประชุม

### Tasks:
- [ ] Database Model: `Booking` (user_id, room_id, start_time, end_time, status, etc.)
- [ ] Database Model: `BookingSnapshot` (เพื่อเก็บประวัติชื่อห้อง/อาคาร ณ วันที่จอง)
- [ ] Pydantic Schemas for Booking
- [ ] Repository: `BookingRepository`
- [ ] Service: `BookingService` (Basic CRUD)
- [ ] API Endpoints: `/bookings` (Create, List, Detail, Cancel)

### Business Rules:
- สมาชิกจองได้เฉพาะห้องที่มีสถานะ `active`
- เวลาจองต้องอยู่ระหว่างช่วงเวลาที่กำหนดในระบบ
- ห้ามจองเวลาในอดีต
