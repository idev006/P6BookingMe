# 11 — Testing Strategy

> กลยุทธ์การทดสอบครอบคลุมทุก layer ของระบบ P6BookingMe

---

## 1. ภาพรวม (Overview)

```
Layer           Tool                  Scope
─────────────────────────────────────────────────────
Unit            pytest (backend)      Service, Repository logic
Integration     pytest + httpx        API endpoints + DB (SQLite in-memory)
E2E             Playwright with AI    User flows บน real browser (Natural Language + Self-healing)
```

**Testing Pyramid:**
```
        /\
       /E2E\        ← น้อย แต่ครอบคลุม happy path
      /──────\
     /Integ   \     ← ปานกลาง ครอบคลุม API contracts
    /──────────\
   /  Unit      \   ← มาก ครอบคลุม business logic
  ──────────────── 
```

---

## 2. Backend Testing (pytest)

### 2.1 Setup

```
backend/
├── pytest.ini
├── tests/
│   ├── __init__.py
│   ├── conftest.py          ← fixtures (DB, client)
│   ├── test_health.py
│   ├── test_auth.py         (เพิ่มเมื่อ implement auth)
│   ├── test_rooms.py        (เพิ่มเมื่อ implement rooms)
│   ├── test_bookings.py     (เพิ่มเมื่อ implement bookings)
│   └── test_users.py        (เพิ่มเมื่อ implement users)
```

**pytest.ini:**
```ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
testpaths = tests
```

### 2.2 Fixtures (conftest.py)

| Fixture | Scope | Description |
|---------|-------|-------------|
| `setup_tables` | function (autouse) | create_all ก่อน test, drop_all หลัง test |
| `db` | function | AsyncSession พร้อม rollback อัตโนมัติ |
| `client` | function | AsyncClient ที่ inject test DB |

### 2.3 Database Strategy

- ใช้ **SQLite in-memory** (`sqlite+aiosqlite:///:memory:`)
- แต่ละ test ได้ตาราง fresh ผ่าน `setup_tables` fixture (autouse=True)
- `db` fixture ทำ rollback หลังแต่ละ test — ไม่มีข้อมูลรั่วระหว่าง tests

### 2.4 Test Patterns

**Pattern 1 — API Integration Test:**
```python
async def test_create_room(client: AsyncClient, db: AsyncSession) -> None:
    # Arrange
    payload = {"name": "Meeting Room A", "capacity": 10, "location": "Floor 1"}
    
    # Act
    response = await client.post("/api/v1/rooms/", json=payload)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Meeting Room A"
    assert "id" in data
```

**Pattern 2 — Authentication Test:**
```python
async def test_login_inactive_user(client: AsyncClient, db: AsyncSession) -> None:
    # Arrange: สร้าง user ที่ยังไม่ active
    user = User(email="test@test.com", status="pending", ...)
    db.add(user)
    await db.commit()
    
    # Act
    response = await client.post("/api/v1/auth/login", json={...})
    
    # Assert: ต้อง reject
    assert response.status_code == 403
```

**Pattern 3 — Business Rule Test:**
```python
async def test_double_booking_rejected(client: AsyncClient, db: AsyncSession) -> None:
    # สร้าง booking แรกที่ confirmed
    # พยายาม book ห้องเดิม เวลาเดียวกัน
    # ต้องได้ 409 Conflict
```

### 2.5 Coverage Targets

| Module | Target |
|--------|--------|
| `app/services/` | ≥ 80% |
| `app/api/v1/endpoints/` | ≥ 70% |
| `app/repositories/` | ≥ 70% |
| Overall | ≥ 70% |

**Run tests:**
```bash
# activate venv ก่อน
pytest                          # run all
pytest -v                       # verbose
pytest tests/test_health.py     # specific file
pytest --cov=app --cov-report=term-missing  # with coverage
```

---

## 3. Frontend Unit Testing (Vitest)

> เพิ่มเมื่อ implement components

### 3.1 Setup
```bash
npm install -D vitest @vue/test-utils @testing-library/vue jsdom
```

### 3.2 Test Patterns

**Component Test:**
```typescript
import { mount } from "@vue/test-utils";
import RoomCard from "@/components/RoomCard.vue";

test("แสดงชื่อห้องและความจุ", () => {
  const wrapper = mount(RoomCard, {
    props: { name: "Meeting Room A", capacity: 10 },
  });
  expect(wrapper.text()).toContain("Meeting Room A");
  expect(wrapper.text()).toContain("10");
});
```

**Pinia Store Test:**
```typescript
import { setActivePinia, createPinia } from "pinia";
import { useAuthStore } from "@/stores/auth";

test("setUser stores user and token in memory", () => {
  setActivePinia(createPinia());
  const store = useAuthStore();
  store.setUser({ id: 1, email: "a@a.com", role: "member" }, "token123");
  expect(store.user?.email).toBe("a@a.com");
  expect(store.token).toBe("token123");
});
```

---

## 4. E2E Testing (Playwright with AI)

### 4.1 Setup (AI Integration)
โครงสร้างโปรเจกต์รองรับการใช้ **Playwright ร่วมกับ AI** (เช่น `zerostep` หรือ `auto-playwright`) ซึ่งมีข้อดีคือ:
1. อ้างอิง UI elements ได้ด้วยภาษามนุษย์ (Natural Language) เช่น `await ai("Click the login button")` 
2. **Self-healing Locators:** เมื่อ UI/CSS เปลี่ยนแปลง AI สามารถหา element ที่ถูกต้องได้เอง ลดภาระการแก้ Test Scripts

```bash
npm install -D @playwright/test @zerostep/playwright
```

```
frontend/
├── playwright.config.ts
└── e2e/
    ├── health.spec.ts          ← ✅ มีแล้ว
    ├── auth.spec.ts            (เพิ่มเมื่อ implement)
    ├── booking.spec.ts         (เพิ่มเมื่อ implement)
    └── admin.spec.ts           (เพิ่มเมื่อ implement)
```

### 4.2 playwright.config.ts

- `baseURL`: `http://localhost:5173`
- มีการโหลด `AI_TOKEN` หรือ `OPENAI_API_KEY` จาก `.env` เพื่อเปิดใช้งาน AI Engine
- `webServer`: start `vite dev` อัตโนมัติ
- Browser: Chromium (primary), Firefox + WebKit (optional CI)
- Trace: `on-first-retry` สำหรับ debug

### 4.3 Test Scenarios (Priority Order)

**P0 — Must Pass (Smoke Tests):**
```
✓ หน้า login โหลดได้
✓ Login สำเร็จ → redirect ไป dashboard
✓ Login ผิด password → แสดง error
✓ Backend health check ตอบสนอง
```

**P1 — Core Flows:**
```
✓ Member จอง booking → สถานะ pending
✓ Approver เห็น list pending → approve → สถานะ confirmed
✓ Member เห็น booking ที่ approved ของตัวเอง
✓ Admin สร้าง/แก้ไข Room
```

**P2 — Edge Cases:**
```
✓ Double-booking → error message
✓ User pending status → ไม่สามารถ login
✓ Session expired → redirect to login
✓ Approver ไม่เห็นเมนู Admin
```

### 4.4 Run E2E Tests

```bash
# ต้องรัน backend ด้วย
# terminal 1
cd backend && uvicorn app.main:app --reload

# terminal 2
cd frontend
npx playwright test                 # run all
npx playwright test --ui            # interactive UI mode
npx playwright test --headed        # แสดง browser
npx playwright show-report          # HTML report
```

---

## 5. CI Pipeline (GitHub Actions — อนาคต)

```yaml
name: CI

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt
      - run: pytest --cov=app
    working-directory: my_workspace/backend

  frontend-e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npx playwright test
    working-directory: my_workspace/frontend
```

---

## 6. Test Naming Conventions

**Backend (pytest):**
```
test_<action>_<context>_<expected_result>
เช่น:
  test_create_booking_with_conflict_returns_409
  test_login_with_pending_user_returns_403
  test_approve_booking_updates_status_to_confirmed
```

**Frontend (Vitest/Playwright):**
```
describe("<ComponentName>") → test("<action> <expected>")
เช่น:
  describe("RoomCard") → test("shows capacity badge")
  describe("Login page") → test("redirects to dashboard on success")
```

---

## 7. Test Data Strategy

- **Backend**: สร้าง test data ใน fixture หรือ `conftest.py` helpers
- **ไม่ใช้ production data** ใน tests เด็ดขาด
- **Factories** (เพิ่มเมื่อ test เยอะขึ้น): ใช้ `pytest-factoryboy` หรือ custom factory functions
- **Seed data**: ถ้า E2E test ต้องการ user/room ที่สร้างล่วงหน้า → สร้างผ่าน API ใน `beforeAll()` hook

---

## 8. สิ่งที่ **ไม่** ทดสอบ

- Framework internals (FastAPI routing, SQLAlchemy ORM เอง)
- Third-party library behavior
- UI pixel-perfect appearance (ใช้ design review แทน)

---

## 9. Checklist ก่อน Merge

- [ ] pytest ผ่านทั้งหมด (0 failures, 0 errors)
- [ ] ไม่มี warning ใหม่ใน pytest output
- [ ] Playwright smoke tests ผ่าน (ถ้ามี UI ที่เกี่ยวข้อง)
- [ ] Coverage ไม่ต่ำกว่า target
