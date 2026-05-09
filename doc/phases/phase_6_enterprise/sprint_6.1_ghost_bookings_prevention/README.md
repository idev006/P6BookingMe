## Sprint 6.1 — Ghost Bookings Prevention ✅

| # | Task | Status |
|---|------|--------|
| 1 | `POST /api/v1/bookings/{id}/check-in` (ยืนยันการใช้ห้อง) | ✅ |
| 2 | Background Job (Celery/APScheduler) Auto-Cancel หากไม่ Check-in ภายใน 15 นาที | ✅ |