# 🚀 P6BookingMe: Enterprise Meeting Room Booking System

P6BookingMe คือระบบจองห้องประชุมระดับองค์กรที่เน้นความสวยงาม (Premium UI), ความปลอดภัย (High Security), และประสิทธิภาพการทำงานของผู้อนุมัติ (Approver Experience)

---

## 🛠️ การติดตั้งระบบ (First Time Setup)

หากคุณดาวน์โหลดโปรเจกต์นี้ไปที่เครื่องใหม่ คุณสามารถติดตั้งทุกอย่างได้โดยอัตโนมัติผ่าน Batch file:

1. **เปิด Terminal** ในโฟลเดอร์ของโปรเจกต์
2. **รันคำสั่ง:**
   ```batch
   setup_environment.bat
   ```
   *สคริปต์นี้จะสร้าง Virtual Environment, ติดตั้ง Dependencies ทั้งหมด และตั้งค่าฐานข้อมูลเริ่มต้นให้ทันที*

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
