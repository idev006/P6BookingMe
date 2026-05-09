# P6BookingMe: Calendar Management Use Cases (Admin)

เอกสารนี้ระบุ Use Cases และข้อกำหนดทางเทคนิคสำหรับการจัดการปฏิทินจองห้องประชุมผ่านหน้าจอ Schedule-X สำหรับผู้ดูแลระบบ (Admin)

## 📋 List of Use Cases

### UC-CAL-01: การกรองข้อมูลขั้นสูง (Advanced Filtering)
*   **เป้าหมาย**: เพื่อให้ Admin สามารถเลือกดูเฉพาะข้อมูลที่ต้องการได้ท่ามกลางรายการจองจำนวนมาก
*   **ฟีเจอร์**:
    *   Dropdown เลือกห้องประชุม (Room Filter)
    *   Dropdown เลือกอาคาร (Building Filter)
    *   Toggle แสดงเฉพาะรายการรออนุมัติ (Pending Only)
*   **สถานะ**: 🔄 กำลังดำเนินการ

### UC-CAL-02: การอนุมัติรายการจองแบบด่วน (Quick Approval)
*   **เป้าหมาย**: เพื่อลดขั้นตอนการสลับหน้าจอ Admin สามารถพิจารณารายการได้โดยตรงจากปฏิทิน
*   **ฟีเจอร์**:
    *   แสดงปุ่ม "Approve" และ "Reject" ใน Event Modal ของ Schedule-X
    *   ใส่เหตุผลการปฏิเสธผ่าน Modal ได้ทันที
*   **สถานะ**: 🔄 กำลังดำเนินการ

### UC-CAL-03: การปรับตารางเวลาแบบลากวาง (Drag & Drop Rescheduling)
*   **เป้าหมาย**: เพื่อความรวดเร็วในการแก้ไขปัญหาตารางจองซ้ำซ้อนหรือการขอเลื่อนเวลาแบบเร่งด่วน
*   **ฟีเจอร์**:
    *   ลาก Event เพื่อเปลี่ยนเวลา (Start/End) หรือเปลี่ยนวัน
    *   ระบบตรวจสอบความขัดแย้ง (Conflict Check) หลังการลากวาง
*   **สถานะ**: 🔄 กำลังดำเนินการ

### UC-CAL-04: การปิดปรับปรุงห้องประชุม (Maintenance Blocking)
*   **เป้าหมาย**: เพื่อป้องกันพนักงานจองห้องในช่วงเวลาที่ห้องไม่พร้อมใช้งาน
*   **ฟีเจอร์**:
    *   Admin สามารถคลิกเลือกช่วงเวลาว่างเพื่อสร้างรายการ "Maintenance"
    *   รายการนี้จะถูก Lock และแสดงผลเป็นสีเทาเข้ม (System Reserved)
*   **สถานะ**: 🔄 กำลังดำเนินการ

### UC-CAL-05: การส่งออกรายงานปฏิทิน (Export Calendar Data)
*   **เป้าหมาย**: เพื่อส่งข้อมูลให้ฝ่ายที่เกี่ยวข้อง (เช่น ฝ่ายอาคาร/แม่บ้าน)
*   **ฟีเจอร์**:
    *   ปุ่ม Export current view เป็น CSV หรือ Excel
    *   กรองข้อมูลตามที่แสดงในหน้าจอปัจจุบัน
*   **สถานะ**: 🔄 กำลังดำเนินการ

---

## 🛠️ Technical Plan
1.  **Frontend**: 
    *   ติดตั้ง `@schedule-x/drag-and-drop`
    *   Implement Custom Modal Component สำหรับ Schedule-X
    *   เพิ่ม Control Panel ด้านบนปฏิทินสำหรับ Filtering & Export
2.  **Backend**:
    *   อัปเดต `/api/v1/calendar` ให้รองรับ Query parameters (room_id, status)
    *   สร้าง Endpoint สำหรับการ Update เวลาจองผ่าน Drag & Drop (PATCH `/bookings/{id}/reschedule`)
