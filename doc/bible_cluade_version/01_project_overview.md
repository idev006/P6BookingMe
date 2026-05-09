# 01 — Project Overview

---

## 1. Vision

> **"ระบบจองห้องประชุมที่เรียบง่าย โปร่งใส และตรวจสอบได้ — ให้ทุกคนในองค์กรสามารถจองห้องได้อย่างมั่นใจ และผู้ดูแลสามารถบริหารจัดการได้อย่างมีประสิทธิภาพ"**

---

## 2. Project Identity

| รายการ | รายละเอียด |
|---|---|
| **ชื่อโปรเจกต์** | P6BookingMe |
| **ประเภท** | Web Application |
| **Frontend** | Vue 3 + Vite (create-vue) + TypeScript + TailwindCSS v4 + DaisyUI v5 |
| **Backend** | Python 3.12 + FastAPI |
| **Database** | SQLite (development) → PostgreSQL (production-ready) |
| **Authentication** | JWT (JSON Web Token) |

---

## 3. Goals (เป้าหมาย)

### Primary Goals
1. **ลดความซับซ้อน** ของการจองห้องประชุมภายในองค์กร — แทนที่การจองผ่าน Line, Email หรือการพูดปากเปล่า
2. **ป้องกันการจองซ้อน** (Double Booking) ด้วย Conflict Check ที่เชื่อถือได้
3. **สร้างความโปร่งใส** — ทุกคนเห็นสถานะการจองห้องแบบ Real-time
4. **ตรวจสอบได้** — ทุกการกระทำมี Audit Trail ที่ชัดเจน

### Secondary Goals
1. ให้ Admin บริหารจัดการห้องและกฎการจองได้ **โดยไม่ต้อง Deploy โค้ด**
2. รองรับการขยายฟีเจอร์ในอนาคต เช่น การแจ้งเตือนผ่าน Email หรือ LINE

---

## 4. Stakeholders

| บทบาท | ความสัมพันธ์กับระบบ |
|---|---|
| **Member (พนักงาน)** | ผู้ใช้งานหลัก — จองและติดตามสถานะการจอง |
| **Approver** | ผู้อนุมัติ — ตรวจสอบและอนุมัติ/ปฏิเสธคำขอจอง |
| **Admin** | ผู้ดูแลระบบ — บริหารห้อง, สมาชิก, กฎ และดู Dashboard |
| **Organization** | เจ้าของระบบ — ต้องการลดการชนกันของการจองและมีข้อมูลสถิติ |

---

## 5. Scope

### ✅ In Scope (สิ่งที่ระบบทำ)

**การจัดการสมาชิก**
- สมัครสมาชิก (พนักงานเท่านั้น), รอ Admin อนุมัติ
- Login / Logout ด้วย JWT
- จัดการโปรไฟล์ส่วนตัว
- Admin กำหนด/ถอด role Approver

**การจองห้องประชุม**
- ค้นหาห้องตาม วันที่, เวลา, ความจุ
- จองห้อง → สถานะ Pending → รอ Approver อนุมัติ
- Approver อนุมัติ / ปฏิเสธ (พร้อมเหตุผล)
- Member ยกเลิกการจองของตัวเอง
- Admin ยกเลิกการจองใดก็ได้
- ป้องกันการจองซ้อนกัน (Conflict Prevention)

**การมองเห็นและติดตาม**
- ปฏิทินภาพรวมการจองของทุกห้อง
- รายการจองพร้อมสถานะของตัวเอง
- การแจ้งเตือนในระบบเมื่อสถานะการจองเปลี่ยน

**การบริหารระบบ (Admin)**
- CRUD ห้องประชุม (ชื่อ, ความจุ, อุปกรณ์, รูปภาพ, สถานที่)
- เปิด/ปิดการใช้งานห้องชั่วคราว
- ตั้งค่ากฎการจอง (จองล่วงหน้า, ระยะเวลาสูงสุด, จำนวนครั้งต่อวัน)
- Dashboard สถิติการใช้ห้อง
- Audit Log ทุกการกระทำสำคัญ

---

### ❌ Out of Scope (สิ่งที่ระบบไม่ทำ ใน Version นี้)

| รายการ | เหตุผล |
|---|---|
| การแจ้งเตือนผ่าน Email / LINE | ต้องการ External Service — เพิ่มใน version ถัดไป |
| การจัดการทรัพยากรเพิ่มเติม (โปรเจกเตอร์, ไมค์) | เกินขอบเขต MVP |
| การชำระเงิน / ค่าบริการห้อง | ไม่ใช่ระบบเชิงพาณิชย์ |
| Mobile Application (iOS/Android) | Web Application เพียงพอสำหรับ Phase 1 |
| การ Sync กับ Google Calendar / Outlook | Phase ถัดไป |
| Multi-tenant (หลายองค์กร) | ออกแบบสำหรับองค์กรเดียว |
| Video Conference Integration (Zoom, Teams) | Phase ถัดไป |

---

## 6. System Context Diagram

```
                        ┌──────────────────┐
                        │   Organization   │
                        │   (เจ้าของระบบ)  │
                        └────────┬─────────┘
                                 │ ใช้งาน
              ┌──────────────────┼──────────────────┐
              │                  │                  │
         ┌────▼─────┐      ┌─────▼──────┐    ┌──────▼────┐
         │  Member  │      │  Approver  │    │   Admin   │
         └────┬─────┘      └─────┬──────┘    └──────┬────┘
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 │ HTTP/REST API
                        ┌────────▼─────────┐
                        │   P6BookingMe    │
                        │   Web Application│
                        │                  │
                        │  ┌────────────┐  │
                        │  │  Frontend  │  │
                        │  │ Vue 3+Vite │  │
                        │  └─────┬──────┘  │
                        │        │ API     │
                        │  ┌─────▼──────┐  │
                        │  │  Backend   │  │
                        │  │  FastAPI   │  │
                        │  └─────┬──────┘  │
                        │        │         │
                        │  ┌─────▼──────┐  │
                        │  │  Database  │  │
                        │  │  SQLite    │  │
                        │  └────────────┘  │
                        └──────────────────┘
```

---

## 7. Key Constraints (ข้อจำกัดสำคัญ)

| ประเภท | รายละเอียด |
|---|---|
| **Technology** | Python 3.12, Virtual Env ที่ `F:\programming\python\P6BookingMe\my_env` |
| **Workspace** | โค้ดและเอกสารทั้งหมดอยู่ใน `my_workspace/` เท่านั้น |
| **Architecture** | Monolith First — แยก Layer ชัดเจนตาม `00_design_philosophy.md` |
| **Simplicity** | YAGNI — ไม่เพิ่ม Redis, Queue, Microservices จนกว่าจะจำเป็น |
| **Documentation** | เอกสารต้องเสร็จก่อนเขียนโค้ดเสมอ |

---

## 8. Definition of Success (MVP)

ระบบถือว่าสำเร็จเมื่อ:

- [ ] พนักงานสามารถ **สมัครสมาชิก** และรอ Admin อนุมัติได้
- [ ] สมาชิกสามารถ **ค้นหาและจองห้องประชุม** ได้
- [ ] Approver สามารถ **อนุมัติหรือปฏิเสธ** การจองได้
- [ ] ระบบ **ป้องกันการจองซ้อน** ได้อย่างน่าเชื่อถือ
- [ ] Admin สามารถ **จัดการห้องและสมาชิก** ได้ผ่าน Admin Panel
- [ ] ทุกการกระทำมี **Audit Trail** บันทึกไว้

---

## 9. Document Index

| เอกสาร | สถานะ |
|---|---|
| `00_design_philosophy.md` | ✅ เสร็จแล้ว |
| `01_project_overview.md` | ✅ เสร็จแล้ว |
| `02_actors_and_usecases.md` | ✅ เสร็จแล้ว |
| `03_requirements.md` | ✅ เสร็จแล้ว |
| `04_system_architecture.md` | ✅ เสร็จแล้ว |
| `05_data_model.md` | ✅ เสร็จแล้ว |
| `06_api_design.md` | ✅ เสร็จแล้ว |
| `07_uml.md` | ✅ เสร็จแล้ว |
| `08_ui_structure.md` | ✅ เสร็จแล้ว |
| `09_security_design.md` | ✅ เสร็จแล้ว |
| `10_adr.md` | ✅ เสร็จแล้ว |
| `11_testing_strategy.md` | ✅ เสร็จแล้ว |
| `12_roadmap.md` | ✅ เสร็จแล้ว |
| `13_deployment_and_devops.md` | ✅ เสร็จแล้ว |
| `14_error_handling_and_logging.md` | ✅ เสร็จแล้ว |
| `15_coding_standards.md` | ✅ เสร็จแล้ว |
| `16_project_management.md` | ✅ เสร็จแล้ว |
