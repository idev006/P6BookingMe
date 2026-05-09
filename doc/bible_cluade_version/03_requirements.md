# 03 — Requirements

---

## 1. Functional Requirements (ความต้องการเชิงฟังก์ชัน)

### FR-01: การจัดการสมาชิก (Member Management)

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-01-01 | ระบบต้องให้พนักงานสมัครสมาชิกโดยกรอก ชื่อ-นามสกุล, อีเมล, รหัสผ่าน, รหัสพนักงาน, หน่วยงาน | Must | Member |
| FR-01-02 | ระบบต้องตรวจสอบว่า Email และรหัสพนักงานไม่ซ้ำกันในระบบ | Must | Member |
| FR-01-03 | Account ที่สมัครใหม่ต้องอยู่ในสถานะ Pending จนกว่า Admin จะอนุมัติ | Must | System |
| FR-01-04 | Member ที่อยู่ในสถานะ Pending ต้องไม่สามารถ Login ได้ | Must | System |
| FR-01-05 | Admin ต้องสามารถ Approve หรือ Reject การสมัครสมาชิกได้ | Must | Admin |
| FR-01-06 | Admin ต้องสามารถ Suspend และ Reactivate account สมาชิกได้ | Must | Admin |
| FR-01-07 | Member ต้องสามารถแก้ไขข้อมูลส่วนตัวได้ (ชื่อ, เบอร์โทร) ยกเว้น Email และรหัสพนักงาน | Must | Member |
| FR-01-08 | ระบบต้องรองรับการ Login ด้วย Email + Password | Must | All |
| FR-01-09 | ระบบต้องรองรับการ Logout และยกเลิก Session ทันที | Must | All |

---

### FR-02: การจัดการห้องประชุม (Room Management)

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-02-01 | Admin ต้องสามารถสร้างห้องประชุมใหม่ได้ โดยกำหนด ชื่อห้อง, ความจุ (คน), สถานที่/อาคาร/ชั้น, คำอธิบาย, อุปกรณ์ | Must | Admin |
| FR-02-02 | Admin ต้องสามารถแก้ไขข้อมูลห้องประชุมได้ | Must | Admin |
| FR-02-03 | Admin ต้องสามารถปิดการใช้งานห้องชั่วคราวได้ (Inactive) โดยไม่ลบข้อมูล | Must | Admin |
| FR-02-04 | ห้องที่ถูกปิดการใช้งาน (Inactive) ต้องไม่ปรากฏในผลการค้นหา | Must | System |
| FR-02-05 | Admin ต้องสามารถอัปโหลดรูปภาพห้องประชุมได้ | Should | Admin |

---

### FR-03: การค้นหาห้องประชุม (Room Search)

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-03-01 | Member ต้องสามารถค้นหาห้องที่ว่างตามวันที่และช่วงเวลาที่ต้องการได้ | Must | Member |
| FR-03-02 | Member ต้องสามารถ filter ห้องตามความจุขั้นต่ำได้ | Must | Member |
| FR-03-03 | Member ต้องสามารถ filter ห้องตามสถานที่/อาคารได้ | Should | Member |
| FR-03-04 | ระบบต้องแสดงเฉพาะห้องที่ว่าง (ไม่มีการจองที่ Confirmed ซ้อนกัน) ในช่วงเวลาที่ค้นหา | Must | System |

---

### FR-04: การจองห้องประชุม (Booking)

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-04-01 | Member ต้องสามารถจองห้องประชุมได้โดยระบุ ห้อง, วันที่, เวลาเริ่ม-สิ้นสุด, หัวข้อการประชุม, จำนวนผู้เข้าร่วม | Must | Member |
| FR-04-02 | ระบบต้องตรวจสอบ Conflict ก่อนสร้าง Booking โดยใช้ Database-level Lock เพื่อป้องกัน Race Condition | Must | System |
| FR-04-03 | Booking ที่สร้างใหม่ต้องอยู่ในสถานะ Pending เสมอ | Must | System |
| FR-04-04 | ระบบต้องบันทึก Snapshot ของข้อมูลห้องและผู้จอง ณ เวลาที่จอง (ชื่อห้อง, ความจุ, ชื่อผู้จอง, หน่วยงาน) | Must | System |
| FR-04-05 | Member ต้องสามารถยกเลิกการจองของตัวเองได้ เมื่อสถานะเป็น Pending หรือ Confirmed | Must | Member |
| FR-04-06 | Admin ต้องสามารถยกเลิกการจองใดก็ได้ พร้อมระบุเหตุผล | Must | Admin |
| FR-04-07 | ระบบต้องบังคับใช้กฎการจองที่ Admin ตั้งค่าไว้ (จองล่วงหน้าสูงสุด, ระยะเวลาสูงสุดต่อครั้ง, จำนวนครั้งต่อวัน) | Must | System |

---

### FR-05: การอนุมัติการจอง (Approval)

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-05-01 | Approver ต้องสามารถดูรายการ Booking ที่อยู่ในสถานะ Pending ทั้งหมดในระบบได้ | Must | Approver |
| FR-05-02 | Approver ต้องสามารถ Approve Booking ได้ → สถานะเปลี่ยนเป็น Confirmed | Must | Approver |
| FR-05-03 | Approver ต้องสามารถ Reject Booking ได้ พร้อมระบุเหตุผลที่บังคับกรอก | Must | Approver |
| FR-05-04 | เมื่อ Approve แล้ว ระบบต้องตรวจสอบ Conflict อีกครั้งก่อน Confirm (กรณีมีการจองซ้อนกันมาในช่วงเวลาเดียวกัน) | Must | System |
| FR-05-05 | Approver ต้องสามารถดูประวัติการอนุมัติของตัวเองได้ | Should | Approver |

---

### FR-06: การแจ้งเตือน (Notification)

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-06-01 | ระบบต้องแจ้งเตือนภายในระบบ (In-app) เมื่อ Booking ของ Member ถูก Approved | Must | System |
| FR-06-02 | ระบบต้องแจ้งเตือนภายในระบบ (In-app) เมื่อ Booking ของ Member ถูก Rejected พร้อมเหตุผล | Must | System |
| FR-06-03 | ระบบต้องแจ้งเตือนภายในระบบ (In-app) เมื่อ Booking ของ Member ถูก Admin ยกเลิก | Must | System |
| FR-06-04 | ระบบต้องแจ้งเตือน Approver เมื่อมี Booking ใหม่รอการอนุมัติ | Should | System |

---

### FR-07: ปฏิทินและการมองเห็น (Calendar & Visibility)

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-07-01 | Member ต้องสามารถดูปฏิทินภาพรวมแสดงการจองของทุกห้องได้ | Must | Member |
| FR-07-02 | ปฏิทินต้องแสดง Time Slot ที่ถูกจอง (Confirmed) และ Pending | Must | System |
| FR-07-03 | Member ต้องสามารถดูรายการการจองของตัวเองพร้อมสถานะได้ | Must | Member |

---

### FR-08: การตั้งค่าระบบ (System Configuration)

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-08-01 | Admin ต้องสามารถตั้งค่าจำนวนวันสูงสุดที่จองล่วงหน้าได้ | Must | Admin |
| FR-08-02 | Admin ต้องสามารถตั้งค่าระยะเวลาสูงสุดต่อการจอง 1 ครั้ง (ชั่วโมง) ได้ | Must | Admin |
| FR-08-03 | Admin ต้องสามารถตั้งค่าจำนวนครั้งสูงสุดที่ Member จองได้ต่อวันได้ | Should | Admin |
| FR-08-04 | การตั้งค่าทั้งหมดต้องมีผลทันทีโดยไม่ต้อง Deploy โค้ดใหม่ | Must | System |

---

### FR-09: Dashboard และรายงาน (Dashboard & Reports)

| ID | Requirement | Priority | Actor |
|---|---|---|---|
| FR-09-01 | Admin ต้องดู Dashboard แสดง: จำนวนการจองวันนี้, การจองรอ Approve, ห้องที่ถูกจองบ่อยที่สุด | Must | Admin |
| FR-09-02 | Admin ต้องสามารถดูรายการ Booking ทั้งหมดในระบบพร้อม filter ตามสถานะ, วันที่, ห้อง, ผู้จอง | Must | Admin |
| FR-09-03 | Admin ต้องสามารถดู Audit Log ของทุกการกระทำสำคัญในระบบ (Who, When, What, Why) | Must | Admin |

---

## 2. Non-Functional Requirements (ความต้องการที่ไม่ใช่ฟังก์ชัน)

### NFR-01: Performance

| ID | Requirement |
|---|---|
| NFR-01-01 | API Response time ต้องไม่เกิน **500ms** สำหรับทุก endpoint ภายใต้ load ปกติ |
| NFR-01-02 | การค้นหาห้องต้องแสดงผลภายใน **1 วินาที** |
| NFR-01-03 | ระบบต้องรองรับ **Concurrent Users** ได้อย่างน้อย 50 คนพร้อมกัน |

---

### NFR-02: Security

| ID | Requirement |
|---|---|
| NFR-02-01 | ทุก API endpoint ต้องมีการ Authenticate ด้วย JWT ยกเว้น `/health`, `/auth/login`, `/auth/register` |
| NFR-02-02 | ทุก Admin endpoint ต้องมีการตรวจสอบ Role `admin` ก่อนเสมอ |
| NFR-02-03 | Password ต้องถูก Hash ด้วย bcrypt ก่อนบันทึกเสมอ — ห้ามบันทึก Plain text |
| NFR-02-04 | JWT Token ต้องหมดอายุภายใน **8 ชั่วโมง** |
| NFR-02-05 | Member ต้องเข้าถึงได้เฉพาะข้อมูล Booking ของตัวเอง ยกเว้นปฏิทินภาพรวม |
| NFR-02-06 | ทุก Input ต้องผ่านการ Validate ด้วย Pydantic (Backend) และ Zod (Frontend) ก่อนประมวลผล |

---

### NFR-03: Reliability

| ID | Requirement |
|---|---|
| NFR-03-01 | ระบบต้องป้องกัน Double Booking ได้ 100% แม้มีการจองพร้อมกัน (Race Condition) |
| NFR-03-02 | ข้อมูล Booking ที่ Confirmed แล้วต้องไม่ถูกแก้ไขหรือลบ — ใช้ Soft Delete และ Status เท่านั้น |
| NFR-03-03 | ทุก Database operation สำคัญต้องอยู่ใน Transaction |

---

### NFR-04: Maintainability

| ID | Requirement |
|---|---|
| NFR-04-01 | โค้ดต้องแยก Layer ตาม `00_design_philosophy.md`: API → Service → Repository |
| NFR-04-02 | Business Logic ต้องอยู่ใน Service Layer เท่านั้น — ห้ามมีใน Router |
| NFR-04-03 | ทุก Configuration ต้องอ่านจาก `.env` ผ่าน `settings` — ห้าม Hardcode |
| NFR-04-04 | ต้องมี Integration Test ครอบคลุม Booking Conflict และ Auth flow |

---

### NFR-05: Usability

| ID | Requirement |
|---|---|
| NFR-05-01 | UI ต้องแสดงสถานะการจองด้วยสีที่ชัดเจน: Pending (เหลือง), Confirmed (เขียว), Rejected (แดง), Cancelled (เทา) |
| NFR-05-02 | Form การจองต้องแสดง Error message ที่อ่านเข้าใจง่าย |
| NFR-05-03 | ระบบต้องรองรับการแสดงผลบน Desktop Browser เป็นหลัก (Chrome, Firefox, Edge) |

---

## 3. User Stories

### Member

| ID | User Story | Acceptance Criteria |
|---|---|---|
| US-M01 | ในฐานะพนักงาน ฉันต้องการสมัครสมาชิก เพื่อเข้าใช้งานระบบจองห้อง | กรอกฟอร์มสมัคร → ได้รับข้อความ "รอการอนุมัติจาก Admin" → ยังไม่สามารถ Login ได้ |
| US-M02 | ในฐานะสมาชิก ฉันต้องการค้นหาห้องว่างตามวันและเวลาที่ต้องการ | ระบุวันที่ + เวลา → เห็นเฉพาะห้องที่ว่างในช่วงนั้น |
| US-M03 | ในฐานะสมาชิก ฉันต้องการจองห้องประชุม เพื่อใช้ประชุมกับทีม | จองสำเร็จ → เห็นสถานะ Pending ในรายการจองของฉัน |
| US-M04 | ในฐานะสมาชิก ฉันต้องการทราบผลการอนุมัติ เพื่อวางแผนล่วงหน้า | รับ Notification เมื่อสถานะเปลี่ยนเป็น Confirmed หรือ Rejected |
| US-M05 | ในฐานะสมาชิก ฉันต้องการยกเลิกการจองที่ไม่ต้องการแล้ว | กดยกเลิก → สถานะเปลี่ยนเป็น Cancelled ทันที |

### Approver

| ID | User Story | Acceptance Criteria |
|---|---|---|
| US-AP01 | ในฐานะ Approver ฉันต้องการเห็นรายการจองที่รออนุมัติ เพื่อจัดการได้รวดเร็ว | เห็นรายการ Pending Bookings พร้อมชื่อผู้จอง, ห้อง, วัน/เวลา |
| US-AP02 | ในฐานะ Approver ฉันต้องการอนุมัติการจอง เพื่อยืนยันการใช้ห้อง | กด Approve → Booking เป็น Confirmed → Member ได้รับแจ้งเตือน |
| US-AP03 | ในฐานะ Approver ฉันต้องการปฏิเสธการจองพร้อมเหตุผล เพื่อให้ Member รับทราบ | กด Reject + กรอกเหตุผล (บังคับ) → Member เห็นเหตุผลใน Notification |

### Admin

| ID | User Story | Acceptance Criteria |
|---|---|---|
| US-AD01 | ในฐานะ Admin ฉันต้องการอนุมัติสมาชิกใหม่ เพื่อควบคุมผู้เข้าใช้งาน | เห็นรายชื่อ Pending Members → กด Approve → Member Login ได้ทันที |
| US-AD02 | ในฐานะ Admin ฉันต้องการเพิ่มห้องประชุมใหม่ เพื่อให้สมาชิกจองได้ | สร้างห้องพร้อมข้อมูลครบ → ห้องปรากฏในระบบค้นหาทันที |
| US-AD03 | ในฐานะ Admin ฉันต้องการดู Dashboard เพื่อติดตามสถานะการใช้ห้องภาพรวม | เห็น: การจองวันนี้, รอ Approve, อัตราการใช้ห้อง |
| US-AD04 | ในฐานะ Admin ฉันต้องการตั้งกฎการจอง เพื่อควบคุมการใช้งานให้เหมาะสม | ตั้งค่า → กฎมีผลทันทีกับการจองครั้งถัดไป |

---

## 4. Business Rules

| ID | Rule |
|---|---|
| BR-01 | ห้องหนึ่งห้องจองได้เพียง 1 การจองต่อ Time Slot เท่านั้น — ห้ามซ้อนกัน |
| BR-02 | Member 1 คน จองได้ไม่เกิน N ครั้งต่อวัน (N กำหนดโดย Admin, default = 3) |
| BR-03 | จองล่วงหน้าได้ไม่เกิน N วัน (N กำหนดโดย Admin, default = 30 วัน) |
| BR-04 | การจองแต่ละครั้งต้องมีระยะเวลาไม่เกิน N ชั่วโมง (N กำหนดโดย Admin, default = 4 ชั่วโมง) |
| BR-05 | เวลาเริ่มต้นการจองต้องไม่ย้อนหลัง (ต้องเป็นอนาคต) |
| BR-06 | เวลาสิ้นสุดต้องมากกว่าเวลาเริ่มต้นเสมอ |
| BR-07 | Member ที่ถูก Suspend ต้องไม่สามารถสร้างการจองใหม่ได้ |
| BR-08 | การยกเลิก Booking ที่ Confirmed ต้องบันทึกเหตุผลเสมอ |
