# Technical Debt Log — P6BookingMe

บันทึกหนี้ทางเทคนิคที่ต้องได้รับการแก้ไขหรือปรับปรุงในภายหลัง (Refactoring / Integrity)

| ID | Issue | Related Sprint | Priority | Planned Phase | Status |
|---|---|---|---|---|---|
| TD001 | `notifications.booking_id` เพิ่ม Foreign Key เชื่อมต่อกับ `bookings` เรียบร้อยแล้ว | Sprint 1.5 | High | Phase 3 | ✅ Resolved |
| TD002 | `UserService` และ `NotificationService` แยกส่วนกันด้วย Event System | Sprint 1.5 | Medium | Phase 5 | ✅ Resolved |
| TD003 | ตาราง `audit_logs` และ `notifications` จะมีขนาดใหญ่ขึ้นเรื่อยๆ ยังไม่มีระบบ Data Archiving | Sprint 1.2/1.5 | Low | Phase 6 | 🔴 Pending |
| TD004 | ระบบ `X-Request-ID` และ Traceability ติดตั้งเรียบร้อยแล้ว | Sprint 1.5.1 | Low | Phase 5 | ✅ Resolved |
| TD005 | ระบบลบห้องประชุมยังไม่ครอบคลุมการลบไฟล์ภาพใน Disk | Sprint 2.2 | High | Phase 2 | ✅ Resolved (Sprint 4.2 Upgrade) |

---
*บันทึกโดย: Project Manager (ตามคำแนะนำของ Auditor อาวุโส — 2026-05-08)*
