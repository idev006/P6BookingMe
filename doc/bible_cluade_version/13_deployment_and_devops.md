# 13 — Deployment and DevOps Strategy

---

## 1. Overview

การออกแบบสถาปัตยกรรมการ Deploy สำหรับระบบ P6BookingMe มุ่งเน้นไปที่ความง่ายในการจัดการ (Simplicity), ความปลอดภัย (Security), และความสามารถในการขยายขนาดในอนาคต (Scalability) แม้ว่าระบบจะเริ่มต้นจากผู้ใช้ระดับองค์กรเดียว แต่โครงสร้างพื้นฐานได้ถูกเตรียมไว้ให้พร้อมสำหรับการทำ CI/CD และ Containerization อย่างเต็มรูปแบบ

---

## 2. Infrastructure Architecture

```mermaid
graph TD
    User([User / Browser])
    
    subgraph "Production Environment (Docker Host)"
        Nginx[Nginx Reverse Proxy]
        
        subgraph "Frontend Container"
            VueApp[Vue 3 SPA (Static Files)]
        end
        
        subgraph "Backend Container"
            FastAPI[FastAPI App + Gunicorn]
        end
        
        subgraph "Database Container"
            PostgreSQL[(PostgreSQL)]
        end
    end
    
    User -- HTTPS / 443 --> Nginx
    Nginx -- Serve Static --> VueApp
    Nginx -- Proxy /api/* --> FastAPI
    FastAPI -- TCP / 5432 --> PostgreSQL
```

---

## 3. Containerization Strategy (Docker)

โปรเจกต์จะใช้ **Docker Compose** เพื่อจัดเตรียมสภาพแวดล้อมที่เหมือนกันตั้งแต่การพัฒนา (Development) ไปจนถึงการใช้งานจริง (Production)

### 3.1 Backend Container
- **Base Image:** `python:3.12-slim` (ลดขนาด image เล็กและปลอดภัย)
- **Server:** ใช้ `gunicorn` คู่กับ `uvicorn` workers สำหรับ Production เพื่อรองรับ Concurrent Requests
- **Environment Variables:** จัดการค่าความลับต่างๆ ผ่านไฟล์ `.env` (ไม่ commit ลง Repository)
- **Volume:** Mount data volume สำหรับเก็บรูปภาพ (`/app/uploads`)

### 3.2 Frontend Container
- **Build Stage:** ใช้ `node:20-alpine` เพื่อติดตั้ง dependencies และทำ `npm run build`
- **Production Stage:** ใช้ `nginx:alpine` เพื่อ serve ไฟล์ static ที่ได้จากการ build
- **Nginx Configuration:** ตั้งค่าให้ทำ Reverse Proxy สำหรับ `/api` ไปยัง Backend Container เพื่อแก้ปัญหา CORS และให้ระบบทำงานบน Port/Domain เดียวกัน

### 3.3 Database Container (Production)
- **Image:** `postgres:16-alpine`
- **Volume:** Mount path ของ database เพื่อไม่ให้ข้อมูลหายเมื่อ Container ถูก restart (`/var/lib/postgresql/data`)

---

## 4. Environment Environments

ระบบแบ่งออกเป็น 2 สภาพแวดล้อมหลัก ได้แก่

| Environment | Database | การรัน Backend | การรัน Frontend | เหมาะสำหรับ |
|---|---|---|---|---|
| **Development** | SQLite (`data/bookingme.db`) | `uvicorn --reload` (Port 8000) | `npm run dev` (Port 5173, Vite HMR) | นักพัฒนาเขียนโค้ดและทดสอบในเครื่อง |
| **Production** | PostgreSQL | Docker + Gunicorn (Port 8000 internal) | Docker + Nginx (Port 80/443) | นำไปใช้งานจริงให้ End-user ใช้งาน |

---

## 5. CI/CD Pipeline (GitHub Actions)

เพื่อรักษาคุณภาพของโค้ดและการส่งมอบที่ราบรื่น (Continuous Delivery) ระบบจะมีการตั้งค่า Pipeline ดังนี้:

### 5.1 Continuous Integration (CI) - ทำงานเมื่อมีการ Push หรือ Pull Request
1. **Linting & Formatting:** ตรวจสอบโค้ดด้วย `flake8` และ `black` สำหรับ Python, `ESLint` และ `Prettier` สำหรับ Frontend
2. **Unit Testing:** รัน `pytest` สำหรับ Backend และ `vitest` สำหรับ Frontend
3. **E2E Testing:** รัน Playwright เพื่อทดสอบ Flow การใช้งานหลัก (Login, สร้าง Booking) บนสภาพแวดล้อมจำลอง
4. **Security Scan:** ตรวจสอบ Dependency ที่มีช่องโหว่ (เช่น `pip-audit`, `npm audit`)

### 5.2 Continuous Deployment (CD) - ทำงานเมื่อ Merge ลง `main` branch
1. **Build Images:** สร้าง Docker Images ของ Frontend และ Backend
2. **Tag & Push:** แปะ Tag version และ Push ไปยัง Container Registry (เช่น GitHub Container Registry)
3. **Deploy Script:** ส่งคำสั่งผ่าน SSH ไปยัง Production Server เพื่อดึง Image ใหม่มารัน (`docker compose pull` และ `docker compose up -d`)

---

## 6. Backup & Recovery Strategy

เนื่องจากระบบ P6BookingMe เป็นระบบที่มีความสำคัญ (จองห้องประชุม) ข้อมูลจึงต้องได้รับการปกป้อง:

1. **Database Backup:**
   - ใช้ `pg_dump` สำรองข้อมูลเป็นไฟล์ `.sql` แบบอัตโนมัติ (Automated Cron Job) ในทุกคืน (02:00 น.)
   - อัปโหลดไฟล์ Backup ไปเก็บยัง Off-site Storage (เช่น AWS S3 หรือระบบ Cloud ภายในองค์กร)
   - นโยบายการเก็บรักษาข้อมูล (Retention Policy): เก็บย้อนหลัง 30 วัน

2. **File / Uploads Backup:**
   - สำรองข้อมูลใน Directory `uploads/` (เช่น รูปภาพห้องประชุม) พร้อมกับ Database เพื่อให้ข้อมูลมีความสอดคล้องกัน

3. **Recovery Test:**
   - ควรกำหนดให้มีการทดสอบกู้คืนข้อมูล (Restore Test) อย่างน้อยไตรมาสละ 1 ครั้ง

---

## 7. Security Configurations in Production

- **HTTPS Only:** Nginx จะรับการเชื่อมต่อผ่านพอร์ต 443 (SSL/TLS) เท่านั้น การเชื่อมต่อพอร์ต 80 จะถูก Redirect มาที่ 443
- **Rate Limiting:** Nginx จะจำกัดจำนวน Request ต่อ IP เพื่อป้องกันการโจมตีแบบ Brute-force และ DDoS ในเบื้องต้น
- **Hidden Headers:** ไม่เปิดเผยเวอร์ชันของ Nginx และ Python/FastAPI ใน HTTP Response Headers (`server_tokens off;`)
- **Secret Management:** รหัสผ่าน Database, JWT Secret, จะถูกตั้งค่าเป็น Environment Variable ที่ฝั่ง Server เท่านั้น ห้าม Hard-code เด็ดขาด
