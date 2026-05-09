# Sprint 4.1 — Dynamic Config Backend 🏃

> พัฒนาระบบจัดเก็บและเรียกใช้การตั้งค่าแบบ Dynamic

### Tasks:
- [ ] Database Model: `SystemConfig` (key, value, type, description)
- [ ] Repository & Service for Config
- [ ] Config Caching Logic (to avoid DB overhead)
- [ ] API Endpoints:
    - `GET /admin/configs` (List all)
    - `PATCH /admin/configs/{key}` (Update value)
- [ ] Integration: Update `BookingService` to use dynamic configs for validation rules

### Initial Configs to Support:
- `ENABLE_CONFLICT_CHECK` (bool)
- `MIN_BOOKING_DURATION_MINS` (int)
- `MAX_BOOKING_DURATION_MINS` (int)
- `ALLOW_PAST_BOOKING` (bool)
