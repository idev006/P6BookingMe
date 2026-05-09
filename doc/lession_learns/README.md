# 🧠 Lessons Learned & Knowledge Base

หน้านี้รวบรวมบทเรียน ความรู้ที่มีค่า และเทคนิคที่ได้รับจากการพัฒนาโครงการ **P6BookingMe** เพื่อใช้เป็นแนวทางในการพัฒนาระบบต่อยอดหรือโครงการอื่นๆ ในอนาคต

---

## 🏛️ 1. Architecture & Design Patterns

### **The Power of Strict Layering**
- **บทเรียน:** การแบ่งเลเยอร์ (API -> Service -> Repository) อาจดูเหมือนมีไฟล์เยอะในช่วงแรก แต่เมื่อโครงการใหญ่ขึ้น มันช่วยให้เรา "ผ่าตัด" ระบบได้ง่ายมาก
- **ตัวอย่าง:** ตอนที่เราเพิ่มระบบสรุปผล (Summary Stats) ใน Sprint 6.4 เราสามารถสร้าง Endpoint ใหม่โดยเรียกใช้ Repository เดิมที่แข็งแกร่งอยู่แล้วได้ทันที

### **Snapshot Pattern (Data Integrity)**
- **บทเรียน:** ข้อมูลที่อ้างอิงกัน (เช่น การจองอ้างอิงชื่อห้อง) ไม่ควรใช้แค่ Foreign Key อย่างเดียวสำหรับประวัติศาสตร์
- **เทคนิค:** เราทำสำเนาข้อมูลสำคัญ (Room Name, User Name) ลงในตาราง Booking โดยตรง เพื่อให้ประวัติการจองยังคงถูกต้องแม้ในอีก 2 ปีข้างหน้าชื่อห้องจะเปลี่ยนไป หรือพนักงานคนนั้นจะลาออกไปแล้ว

---

## 🎨 2. UI/UX & Aesthetics (World Class Standards)

### **The Cockpit Principle (หลักการห้องนักบิน)**
- **บทเรียน:** ผู้ดูแลระบบหรือผู้อนุมัติไม่ต้องการ "แค่ตารางข้อมูล" แต่ต้องการ "ข้อมูลเพื่อการตัดสินใจ"
- **การนำไปใช้:** การสร้าง Approver Dashboard ที่สรุปตัวเลข Pending และกราฟสถิติ ช่วยให้เขารู้ว่าต้องจัดการอะไรก่อน-หลังโดยไม่ต้องไล่ดูทีละรายการ

### **Context-Aware Actions**
- **บทเรียน:** การกด "อนุมัติ" ไม่ควรต้องเปลี่ยนหน้าไปมา
- **เทคนิค:** การรวมปุ่ม Approve/Reject เข้าไปใน **BookingDetailModal** ทำให้ผู้อนุมัติสามารถพิจารณาจากหน้าปฏิทิน (Calendar) หรือหน้าประวัติ (History) ได้ทันที ช่วยลด Click-rate และเพิ่มประสิทธิภาพในการทำงาน

---

## 🛡️ 3. Security & Stability

### **Defense in Depth (การป้องกันหลายชั้น)**
- **บทเรียน:** Security ใน Frontend คือ UX, Security ใน Backend คือของจริง
- **การนำไปใช้:** แม้เราจะซ่อนเมนู Admin ในหน้าจอ แต่ใน Backend ทุก Endpoint ต้องมี `require_admin` หรือ `require_approver` ที่ตรวจสอบจากฐานข้อมูลเสมอ ป้องกันการแฮ็ก Role ผ่านเบราว์เซอร์

### **Race Condition Prevention**
- **บทเรียน:** ในระบบจอง "ความเร็ว" ของการกดมีผล
- **เทคนิค:** ใช้ `SELECT ... FOR UPDATE` ในระดับ Database เพื่อล็อคคิวไม่ให้มีการจองซ้อนกันในช่วงเสี้ยววินาที (Conflict Prevention)

---

## 🚀 4. Sprint-Specific Insights

- [Sprint 6.4: Approver Experience Optimization](./sprint_6.4_approver_experience.md)
- [Remote Access: Cloudflare Tunnel, CORS & Trailing Slashes](./cloudflare_tunnel_cors_and_redirects.md)
