# 🚀 P6BookingMe: Enterprise Meeting Room Booking System

P6BookingMe คือระบบจองห้องประชุมระดับองค์กรที่เน้นความสวยงาม (Premium UI), ความปลอดภัย (High Security), และประสิทธิภาพการทำงานของผู้อนุมัติ (Approver Experience)

---

## 🛠️ ขั้นตอนการติดตั้ง (Installation Workflow)

เพื่อให้ระบบทำงานได้อย่างถูกต้อง โปรดทำตาม 5 ขั้นตอนนี้ครับ:

1. **สร้างโฟลเดอร์หลัก (Parent Folder):** 
   สร้างโฟลเดอร์ชื่อโครงการ เช่น `P6BookingMe` ไว้ในเครื่องของคุณ
2. **ดาวน์โหลด Source Code:** 
   เข้าไปที่โฟลเดอร์ในข้อ 1 แล้วรันคำสั่งเพื่อดาวน์โหลดโค้ดลงในโฟลเดอร์ `my_workspace`:
   ```bash
   git clone https://github.com/idev006/P6BookingMe.git my_workspace
   ```
   *(หมายเหตุ: ต้องมีคำว่า `my_workspace` ต่อท้าย เพื่อให้ Git สร้างชื่อโฟลเดอร์ให้ตรงกับระบบ)*

3. **รันสคริปต์ติดตั้ง:** 
   เข้าไปในโฟลเดอร์ `my_workspace` ที่เพิ่งได้มา แล้วรันไฟล์:
   ```batch
   setup_environment.bat
   ```
   *สคริปต์นี้จะสร้าง Virtual Environment ชื่อ `my_env` ไว้ที่โฟลเดอร์หลัก (Parent), ติดตั้ง Dependencies และตั้งค่าฐานข้อมูลให้โดยอัตโนมัติ*
4. **ติดตั้งส่วนอื่นๆ:** ระบบจะจัดการ Node modules และค่าคอนฟิกต่างๆ ให้พร้อมใช้งาน
5. **เริ่มระบบ:** รัน `run_all_dev.bat` เพื่อเริ่มต้นใช้งาน

---

## 💻 วิธีการรันระบบ (How to Run)

เมื่อติดตั้งเสร็จแล้ว คุณสามารถเริ่มทำงานได้ด้วยคำสั่งเดียว:

```batch
run_all_dev.bat
```
*คำสั่งนี้จะเปิดหน้าต่างแยกสำหรับ Backend และ Frontend พร้อมกัน*

---

## 📁 โครงสร้างโปรเจกต์ (Project Structure)

- `backend/`: FastAPI Application (Python 3.12)
  - `app/`: Source code แบ่งเป็น API, Service, Repository Layers
  - `alembic/`: Database Migrations
- `frontend/`: Vue 3 + Vite + TailwindCSS 4 Application
  - `src/`: Source code แบ่งเป็น Components, Stores, Services
- `doc/`: เอกสารโครงการและบทเรียนที่ได้รับ (Lessons Learned)

---

## 🔑 ข้อมูลเบื้องต้นสำหรับการทดสอบ

| Role | Username (Email) | Password |
|------|------------------|----------|
| **Admin** | `admin@p6booking.me` | `admin1234` |
| **Approver** | `approver@p6booking.me` | `password123` |
| **Member** | `user@p6booking.me` | `password123` |

---

## 🛡️ เทคโนโลยีที่ใช้ (Tech Stack)

- **Backend:** FastAPI, SQLAlchemy (Async), Pydantic v2, JWT Auth
- **Frontend:** Vue 3 (Composition API), Pinia, TailwindCSS v4, DaisyUI v5, Lucide Icons
- **Database:** SQLite (Development) / PostgreSQL (Production ready)
- **Deployment:** Docker support available

---

**Happy Booking!** 🚀
