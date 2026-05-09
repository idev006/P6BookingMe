# 14 — Error Handling and Logging Strategy

---

## 1. Overview

การจัดการข้อผิดพลาด (Error Handling) และการบันทึกเหตุการณ์ (Logging) เป็นสิ่งสำคัญสำหรับการบำรุงรักษาระบบและค้นหาสาเหตุของปัญหาในระดับ Production ระบบ P6BookingMe จะกำหนดมาตรฐานการตอบกลับ API เมื่อเกิด Error ให้เป็นรูปแบบเดียวกันทั้งหมด และกำหนดวิธีการบันทึก Log ให้เป็นโครงสร้าง (Structured Logging)

---

## 2. Standard API Error Response

ทุกครั้งที่ระบบเกิดข้อผิดพลาด API ต้องตอบกลับด้วย JSON Format ที่มีโครงสร้างตายตัว เพื่อให้ Frontend สามารถนำไปแสดงผลได้อย่างถูกต้องเสมอ

### 2.1 Error Format Template (Flat Structure)

```json
{
  "detail": "Human readable error message",
  "error_code": "ERROR_CODE_STRING",
  "path": "/api/v1/resource"
}
```

- **`detail`**: ข้อความอธิบายเบื้องต้นสำหรับนักพัฒนา (Developer-friendly) หรือผู้ใช้
- **`error_code`**: รหัสข้อผิดพลาดแบบตัวอักษร (String) ใช้สำหรับ Frontend นำไปจับคู่ (Map) กับข้อความแปลภาษาหรือใช้ประมวลผลเชิงตรรกะ
- **`path`**: URL Path ที่เกิดข้อผิดพลาด เพื่อช่วยในการ Debugging

### 2.2 ตัวอย่างการตอบกลับ

**422 Validation Error (Pydantic ValidationError)**
```json
{
  "detail": "ข้อมูลที่ส่งมาไม่ถูกต้อง (Validation Error)",
  "errors": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ],
  "path": "/api/v1/auth/register"
}
```

**409 Conflict Error (ตัวอย่างการจองเวลาชนกัน)**
```json
{
  "detail": "The selected time slot overlaps with an existing confirmed booking.",
  "error_code": "BOOKING_CONFLICT",
  "path": "/api/v1/bookings"
}
```

**401 Unauthorized Error**
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token",
    "details": null
  }
}
```

---

## 3. Global Exception Handler (FastAPI)

ที่ฝั่ง Backend จะมีการลงทะเบียน Global Exception Handler เพื่อดักจับ Exception ก่อนจะส่งกลับไปหาผู้ใช้:

1. **`HTTPException` Handler:** แปลงค่า `status_code` และ `detail` ให้มาอยู่ในรูปแบบ JSON Standard
2. **`RequestValidationError` Handler:** ดักจับ Pydantic Error และแปลงเป็นรูปแบบ Standard (`code: "VALIDATION_ERROR"`)
3. **`Exception` (Unhandled) Handler:** ดักจับ Internal Server Error (500) แบบไม่คาดคิด โดยจะส่ง `code: "INTERNAL_SERVER_ERROR"` ออกไปหาผู้ใช้ แต่จะแสดงข้อความว่า "Something went wrong" เพื่อความปลอดภัย และ **บันทึก Stack Trace ลง Log เท่านั้น**

---

## 4. Logging Strategy

การทำ Logging จะใช้แบบ **Structured Logging** (แนะนำ library `structlog` หรือ `loguru`) เพื่อง่ายต่อการนำข้อมูลไปวิเคราะห์ต่อด้วยเครื่องมืออย่าง ELK Stack (Elasticsearch, Logstash, Kibana) หรือ Datadog

### 4.1 รูปแบบ Log (JSON Format ใน Production)
```json
{
  "timestamp": "2026-05-08T12:00:00.000Z",
  "level": "INFO",
  "request_id": "req-1234abcd",
  "user_id": 42,
  "action": "booking.create",
  "message": "Booking created successfully",
  "room_id": 5
}
```

### 4.2 สิ่งที่ต้องทำการบันทึก (What to log)
- **INFO:** เหตุการณ์สำคัญทางธุรกิจ (Business Events) เช่น มีคนสมัครสมาชิกใหม่, การจองสำเร็จ, การอนุมัติการจอง
- **WARNING:** เหตุการณ์ที่ผิดปกติแต่ระบบทำงานต่อได้ เช่น ไม่สามารถส่ง Notification ได้ (แต่อนุมัติสำเร็จแล้ว), ผู้ใช้พยายามล็อกอินผิดรหัสหลายครั้ง
- **ERROR:** ข้อผิดพลาดที่มีผลกระทบกับการทำงาน (Exceptions) เช่น ติดต่อฐานข้อมูลไม่ได้, การเชื่อมต่อถูกตัดขาด
- **DEBUG:** ข้อมูลเพิ่มเติมสำหรับการค้นหาปัญหา (เปิดเฉพาะตอน Development) เช่น Query SQL

### 4.3 ข้อควรระวัง (Security)
- **ห้ามบันทึกรหัสผ่าน (Password)**
- **ห้ามบันทึก JWT Access Token**
- ห้ามบันทึกข้อมูลส่วนบุคคลที่ไวต่อความรู้สึก (PII) ลงใน Log แบบ Plain text ถ้าไม่จำเป็น

---

## 5. Request IDs

เพื่อการตามรอย (Traceability) ระบบจะเพิ่ม Middleware ในการสร้าง `X-Request-ID` สุ่มขึ้นมาทุกครั้งที่มี HTTP Request วิ่งเข้ามา และแนบ ID นั้นไปกับการเขียน Log ทุกบรรทัดที่เกิดใน Lifecycle ของ Request นั้น

สิ่งนี้จะช่วยให้เวลาเกิด Error 500 ระบบตอบ Request ID กลับไปให้ผู้ใช้ (หรือ Frontend นำไปแสดงผลให้ Admin) จากนั้น Admin สามารถนำ ID นั้นไปเสิร์ชหา Stack Trace ใน Log ได้ทันที
