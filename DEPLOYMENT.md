# P6BookingMe Deployment Guide 🚀

ยินดีด้วย! ระบบจองห้องประชุม P6BookingMe ของคุณพร้อมใช้งานแล้ว นี่คือสรุปขั้นตอนการติดตั้งและรันระบบทั้ง Backend และ Frontend

## 🛠️ 1. Backend Setup (FastAPI)

1. **ติดตั้ง Dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. **ตั้งค่า Environment:**
   - สร้างไฟล์ `.env` โดยคัดลอกจาก `.env.example`
   - ตรวจสอบ `DATABASE_URL` และ `SECRET_KEY`
3. **Database Migration:**
   ```bash
   alembic upgrade head
   ```
4. **Seed ข้อมูลเริ่มต้น (สำคัญ):**
   ```bash
   python scripts/seed_configs.py  # ตั้งค่าระบบแบบ Dynamic
   # python scripts/seed_admin.py # (ถ้ามีสคริปต์สร้าง Admin)
   ```
5. **เริ่ม Server:**
   ```bash
   uvicorn app.main:app --reload
   ```

## 💻 2. Frontend Setup (Vue 3 + Vite)

1. **ติดตั้ง Dependencies:**
   ```bash
   cd frontend
   npm install
   ```
2. **เริ่มระบบ Development:**
   ```bash
   npm run dev
   ```
3. **เข้าใช้งาน:** เปิด Browser ไปที่ `http://localhost:5173`

## 🔍 3. Verification (ตรวจสอบความพร้อม)

คุณสามารถรันสคริปต์เพื่อตรวจสอบว่าระบบทำงานถูกต้องหรือไม่:
```bash
cd backend
python scripts/health_check.py
```

---

## 🛡️ Security Note
- ในการใช้งานจริง (Production) ควรเปลี่ยน `SECRET_KEY` ให้เป็นค่าที่ปลอดภัย
- ตรวจสอบให้แน่ใจว่าโฟลเดอร์ `uploads/` มีสิทธิ์เขียนไฟล์ (Write Permission) สำหรับรูปภาพห้องประชุม

**Happy Booking!** 🚀
