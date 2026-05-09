# Phase: Stabilization for Cloudflare Tunnel Connectivity

## 1. Overview
วัตถุประสงค์ของเฟสนี้คือการทำให้ระบบ P6BookingMe สามารถใช้งานผ่าน Cloudflare Tunnel (HTTPS) ได้อย่างเสถียร 100% โดยแก้ปัญหาเรื่องการรั่วไหลของ Local Origin (localhost:8000), ปัญหา CORS, และ Mixed Content (HTTP/HTTPS)

## 2. Problems Encountered (ปัญหาที่พบ)

### 2.1 Origin Leakage via Redirects (URL รั่วไหล)
- **อาการ**: เมื่อเรียก API บางเส้นทาง (เช่น `/auth/login`) Backend จะสั่ง 307/308 Redirect ไปยังเวอร์ชันที่มี Slash ปิดท้าย (`/auth/login/`)
- **สาเหตุ**: ใน Redirect Header ของ FastAPI จะระบุค่า `Location` เป็น Absolute URL ของเครื่อง Internal (เช่น `http://localhost:8000/auth/login/`) ทำให้ Browser ของผู้ใช้ที่เข้าผ่าน Tunnel พยายามวิ่งไปหา localhost ของตัวเอง ซึ่งไม่มีอยู่จริง

### 2.2 Mixed Content Errors
- **อาการ**: Browser บล็อกการโหลดรูปภาพหรือการเรียก API บางจุด
- **สาเหตุ**: หน้าเว็บโหลดผ่าน `https://...` แต่ตัวโค้ดมีการเรียกทรัพยากรผ่าน `http://localhost:8000` ทำให้เกิดความไม่ปลอดภัย และ Browser ไม่อนุญาตให้ทำงาน

### 2.3 Broken Image Paths
- **อาการ**: รูปภาพห้องประชุมและรูปโปรไฟล์ไม่แสดงผลเมื่อเข้าผ่าน Tunnel
- **สาเหตุ**: พาธของรูปภาพถูกเก็บเป็นพาธภายใน และ Frontend เรียกใช้โดยตรงผ่าน Port 8000 ของเครื่อง Server

## 3. Implementation Details (การแก้ไข)

### 3.1 Trailing Slash Standardization (มาตรฐาน Slash ปิดท้าย)
เราได้ทำการปรับแต่งทั้ง **Backend** และ **Frontend** ให้ใช้มาตรฐานเดียวกันคือมี Slash ปิดท้ายทุกเส้นทางที่เป็น Collection หรือ Action:
- **Backend Update**: เปลี่ยน `@router.post("/login")` เป็น `@router.post("/login/")` ในทุกไฟล์ Endpoint
- **Frontend Update**: ปรับการเรียก Axios ทั้งหมดให้ลงท้ายด้วย `/` (เช่น `api.post('/auth/login/')`)
- **ผลลัพธ์**: แก้ปัญหาการ Redirect และการรั่วไหลของ URL ได้ถาวร

### 3.2 Relative Path & Vite Proxy
- **Config**: ปรับ `VITE_API_URL=/api/v1` (ไม่ระบุ Domain)
- **Vite Proxy**: ใช้ `vite.config.ts` ทำหน้าที่เป็น Reverse Proxy ส่งต่อ `/api` ไปยัง `http://localhost:8000` ภายในเครื่อง Server
- **ผลลัพธ์**: Browser จะสื่อสารผ่าน Tunnel Domain เพียงอย่างเดียว ไม่มีการเรียกหา localhost โดยตรงอีก

### 3.3 Image Path Normalization
- **Utility**: ใช้ `getImageUrl` ใน `format.ts` เพื่อจัดการพาธรูปภาพให้เป็น Relative เสมอ
- **ผลลัพธ์**: รูปภาพจะโหลดผ่าน Proxy ตัวเดียวกับ API ทำให้ใช้งาน HTTPS ได้โดยอัตโนมัติ

## 4. Standardized API Routes (สรุปเส้นทางมาตรฐาน)

| ประเภท | รูปแบบที่ถูกต้อง (Correct) | ตัวอย่าง |
| :--- | :--- | :--- |
| **Collection** | มี `/` ปิดท้าย | `/rooms/`, `/bookings/`, `/admin/users/` |
| **Actions** | มี `/` ปิดท้าย | `/approve/`, `/cancel/`, `/reschedule/` |
| **Resource ID** | **ไม่มี** `/` ปิดท้าย | `/rooms/1`, `/bookings/123` |

## 5. Verification Results
- ✅ **Login/Register**: ผ่าน Tunnel ได้ทันที ไม่โดน Redirect ออกข้างนอก
- ✅ **Admin Dashboard**: โหลดข้อมูลและ Export รายงานได้ปกติ
- ✅ **Booking Actions**: การอนุมัติและการยกเลิกทำงานได้เสถียร
- ✅ **Media**: รูปภาพแสดงผลครบถ้วนภายใต้ HTTPS

---
*Documented on: 2026-05-09*
*Phase Status: COMPLETED*
