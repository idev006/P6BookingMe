# 16 — Project Management & Tracking Plan

> แผนบริหารจัดการโครงการ เพื่อให้การทำงานร่วมกันระหว่าง ผู้ใช้งาน (Product Owner) และ AI (Lead Developer/PM) มีประสิทธิภาพสูงสุด และสามารถ **Tracking ความคืบหน้าได้แบบ Real-time**

---

## 1. Project Management Framework (Agile / Kanban)

ระบบจะใช้แนวคิด Agile โดยอิงจาก **Sprint** ที่ถูกวางไว้ใน `12_roadmap.md` แต่เพิ่มกลไกการติดตามแบบ Kanban (Micro-level) เพื่อให้เห็นสถานะของงานแต่ละชิ้นอย่างชัดเจน

**Roles:**
- **User:** รับบทบาทเป็น **Product Owner (PO)** ผู้กำหนดทิศทาง ตัดสินใจ Business Logic และเป็นผู้ตรวจสอบ (Reviewer) ขั้นสุดท้าย
- **AI:** รับบทบาทเป็น **Lead Developer & Scrum Master** ผู้รับผิดชอบการเขียนโค้ด ทดสอบ และอัปเดตสถานะโครงการ

---

## 2. Tracking Mechanism (เครื่องมือติดตามความคืบหน้า)

เพื่อให้สามารถ Track ได้เสมอ เราจะใช้สถาปัตยกรรมเอกสาร 3 ระดับ:

### 2.1 Macro Level (ระดับโครงสร้างภาพรวม)
- **เครื่องมือ:** ไฟล์ `12_roadmap.md`
- **วิธีใช้:** อัปเดตเมื่อจบแต่ละ Sprint (เปลี่ยน `⬜` เป็น `✅`) และใช้วัดเปอร์เซ็นต์ความสำเร็จของทั้ง Phase

### 2.2 Micro Level (ระดับปฏิบัติการประจำวัน)
- **เครื่องมือ:** ไฟล์ `TRACKER.md` (จะถูกสร้างไว้ที่ Root Directory ของโปรเจกต์ `my_workspace/TRACKER.md`)
- **วิธีใช้:** เปรียบเสมือน **Kanban Board** ที่แบ่งสถานะงานเป็น:
  - `[ ] TODO`: งานที่ต้องทำใน Sprint ปัจจุบัน
  - `[>] IN PROGRESS`: งานที่ AI กับ User กำลังทำร่วมกันในเซสชันนี้
  - `[?] REVIEW`: โค้ดเสร็จแล้ว รอ User รันและตรวจสอบ
  - `[x] DONE`: งานผ่านการทดสอบและสมบูรณ์แล้ว

### 2.3 Version Control Level (ระดับโค้ด)
- **เครื่องมือ:** Git + Conventional Commits
- **วิธีใช้:** ทุกครั้งที่ปิด Task ใน Tracker AI จะแจ้งให้ User สั่ง Commit โดยใช้ Tag ที่ผูกกับ Sprint เสมอ เช่น:
  - `feat(auth): [Sprint 1.1] add User database model`
  - `test(booking): [Sprint 3.2] add pytest for booking conflicts`

---

## 3. Definition of Done (DoD) - นิยามของคำว่า "เสร็จ"

Task หนึ่งชิ้นใน `TRACKER.md` จะถูกเปลี่ยนสถานะเป็น `[x] DONE` ได้ ก็ต่อเมื่อผ่านเงื่อนไข 4 ข้อนี้เท่านั้น (Quality Control):

1. **Code Execution:** รันโค้ดได้โดยไม่เกิด Syntax Error
2. **Testing Pass:** 
   - Backend ต้องมี Test และผ่านการรัน `pytest`
   - Frontend ต้องผ่าน E2E Testing ด้วย `Playwright` 
3. **Standard Compliant:** โค้ดปฏิบัติตามกฎใน `15_coding_standards.md` และ `09_security_design.md` (เช่น ไม่มี Raw SQL, รหัสผ่านถูก Hash)
4. **PO Approved:** User ยืนยันว่าผลลัพธ์ตรงตามความต้องการ

---

## 4. Execution Workflow (วงจรการทำงานรายเซสชัน)

เพื่อให้โครงการไม่หลงทิศทาง ทุกครั้งที่เราเริ่มคุยกัน (หรือขึ้นฟีเจอร์ใหม่) เราจะทำตาม 4 ขั้นตอนนี้เสมอ:

| ขั้นตอน | ผู้ทำ | รายละเอียด |
|---|---|---|
| **1. Sync & Pick** | AI + User | AI จะเปิดอ่าน `TRACKER.md` และเสนอ Task ถัดไป (ที่มีสถานะ TODO) ให้ User อนุมัติเริ่มงาน |
| **2. Code & Test** | AI | AI ดำเนินการสร้างไฟล์ เขียนโค้ด และเขียน Test Script (Pytest / Playwright) |
| **3. Review** | User | User ลองรันโค้ด หรือตรวจสอบผ่านเบราว์เซอร์ หากเจอบัคแจ้ง AI แก้ไข |
| **4. Update Board**| AI | เมื่อผ่านการ Review AI จะไปอัปเดต `TRACKER.md` ให้เป็น DONE และแนะนำคำสั่ง Git Commit |

---

## 5. Risk Management (การจัดการความเสี่ยง)

ในฐานะ Auditor ผมได้วางแผนรับมือปัญหาที่อาจทำให้โครงการสะดุดไว้ดังนี้:
1. **Technical Debt:** หากมีจุดที่ต้องข้ามไปก่อน (เช่น "เดี๋ยวค่อยทำ UI สวยๆ ทีหลัง") เราจะเปิด Issue ไว้ในส่วน `Backlog` ของ TRACKER เสมอ จะไม่มีการทำหล่นหาย
2. **Scope Creep:** หาก User อยากได้ฟีเจอร์ใหม่ที่ไม่ได้อยู่ใน Requirements ดั้งเดิม AI จะแนะนำให้บันทึกไว้ใน `Phase 6 — Enterprise Scale` แทนการแทรกกลาง Sprint เพื่อให้ MVP เสร็จตามกำหนด
3. **AI Context Loss:** หากข้อความยาวเกินไปและ AI เริ่มลืมบริบท ระบบ Track ผ่านไฟล์ `TRACKER.md` จะทำหน้าที่ดึงความทรงจำของ AI กลับมาสู่ปัจจุบันเสมอ

---
