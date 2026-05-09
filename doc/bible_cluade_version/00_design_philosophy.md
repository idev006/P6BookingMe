# 00 — System Design Philosophy

---

## 🏛️ ปรัชญาการออกแบบสถาปัตยกรรม (Architecture Philosophy)

เพื่อความยั่งยืน ความปลอดภัย และความง่ายในการบำรุงรักษาระบบ **P6BookingMe** เรายึดถือหลักการดังต่อไปนี้:

---

### 1. การแบ่งเป็น Layer ที่มีหน้าที่เฉพาะ (Strict Layering)

ระบบถูกออกแบบให้แยกหน้าที่กันอย่างเด็ดขาด (Separation of Concerns) เพื่อลดความซับซ้อน:

- **API Layer (Router):** รับ/ส่งข้อมูลผ่าน Protocol (HTTP/REST) และจัดการเรื่อง Authentication เท่านั้น ไม่มี Business Logic
- **Service Layer (Business Logic):** หัวใจของระบบ — จัดการกฎการจอง เช่น การตรวจสอบห้องว่าง (Availability Check), การป้องกันการจองซ้อน (Conflict Prevention), และ Workflow การอนุมัติ
- **Engine Layer (Internal Tools):** งานเฉพาะทาง เช่น Notification Engine (Email/LINE), Calendar Engine สำหรับคำนวณ Time Slot, หรือ Report Engine สำหรับสรุปการใช้ห้องประชุม
- **Data Access Layer (Repository/Models):** จัดการการคุยกับ Database และความถูกต้องของ Schema

---

### 2. การสื่อสารด้วย Contract ระหว่าง Layer (Contract-Driven)

แต่ละ Layer จะไม่คุยกันด้วย "ดิบ" (Raw Data) แต่จะคุยกันผ่าน "สัญญา" ที่ตกลงกันไว้:

- ใช้ **Pydantic Schemas (Backend)** และ **TypeScript Interfaces/Zod (Frontend)** เป็น Protocol หลัก
- ข้อมูลจาก Database จะถูกแปลงเป็น Schema ก่อนส่งออกเสมอ — ป้องกัน internal field รั่วไหล
- การสื่อสารภายใน Layer ต้องชัดเจน มีการส่งผ่านข้อมูลที่ผ่านการ Validate แล้วเท่านั้น

---

### 3. Loose Coupling (ความไม่ผูกติดกัน)

แต่ละส่วนประกอบต้องสามารถทำงานได้โดยพึ่งพาผู้อื่นให้น้อยที่สุด:

- **Interchangeable:** เราต้องสามารถเปลี่ยน Library ใน Engine Layer ได้ (เช่น เปลี่ยน Notification provider จาก LINE เป็น Email) โดยไม่กระทบ Service หรือ API
- **Independent Testing:** แต่ละ Layer ต้องสามารถเขียน Test แยกกันได้
- **Framework Agnostic:** Business Logic สำคัญ (เช่น การคำนวณ Time Slot หรือ Conflict Check) ต้องไม่ผูกติดกับ FastAPI หรือ Vite มากเกินไป เพื่อให้ง่ายต่อการย้ายหรืออัปเกรดในอนาคต

---

### 4. Booking Integrity & Snapshot (ความถูกต้องของข้อมูลการจอง)

ข้อมูลการจองต้องมีความถูกต้องแม่นยำและตรวจสอบได้ตลอดเวลา:

- **Snapshot Pattern:** เมื่อการจองได้รับการยืนยัน ข้อมูลที่เกี่ยวข้อง (เช่น ชื่อห้อง, ความจุ, ชื่อผู้จอง, ชื่อหน่วยงาน, วัตถุประสงค์) ต้องถูก "ทำสำเนา" ลงใน Booking record โดยตรง — ไม่ใช่แค่ Foreign Key ไปยัง Room หรือ User เพื่อให้ข้อมูลการจองยังคงถูกต้องแม้ห้องหรือผู้ใช้จะถูกแก้ไขในภายหลัง
- **Conflict-Safe Write:** การสร้างการจองต้องใช้ Database-level Lock หรือ Transaction เพื่อป้องกัน Race Condition จากการจองพร้อมกัน
- **Immutability:** การจองที่ "Confirmed" แล้วจะไม่ถูกลบ แต่จะใช้สถานะ "Cancelled" หรือ "Modified" แทน เพื่อรักษา Audit Trail

---

### 5. Auditability & Traceability (การตรวจสอบย้อนกลับ)

ทุกการกระทำที่มีผลต่อสถานะของการจองต้องมีร่องรอยเสมอ:

- **Booking History:** บันทึก Who, When, What และ Why (เหตุผลการยกเลิก/แก้ไข) ในทุกขั้นตอนสำคัญ
- **Status Transition Log:** บันทึกการเปลี่ยนสถานะทุกครั้ง เช่น `Pending → Confirmed → Cancelled` พร้อม timestamp และผู้กระทำ
- **Digital Footprint:** บันทึก IP Address และ User Agent เพื่อความปลอดภัยและการตรวจสอบ

---

### 6. Simplicity over Over-Engineering (เน้นความเรียบง่าย)

เลือกใช้วิธีการที่ซับซ้อนน้อยที่สุดที่ยังสามารถแก้ปัญหาได้ (Keep It Simple, Stupid):

- **YAGNI (You Ain't Gonna Need It):** ไม่เพิ่มระบบที่ซับซ้อน (เช่น Redis Cache, Message Queue, Microservices) หากโหลดของระบบยังไม่ถึงจุดที่จำเป็น — ระบบจองห้องประชุมภายในองค์กรมักไม่ต้องการ Scale ระดับ Netflix
- **Monolith First:** เริ่มต้นด้วยโครงสร้างที่จัดการง่ายในก้อนเดียว แต่แยก Layer ให้ดีเพื่อให้แยกส่วนได้ง่ายในอนาคต
- **Polling ก่อน WebSocket:** ใช้ Polling สำหรับ Real-time updates ก่อน หากผู้ใช้บ่น latency ค่อยเปลี่ยน

---

### 7. Agile & Iterative Development (ก้าวหน้าอย่างต่อเนื่อง)

เราเชื่อในการส่งมอบคุณค่าทีละน้อยแต่สม่ำเสมอ แทนการทำโปรเจกต์ขนาดใหญ่ในครั้งเดียว:

- **Small Sprints:** แบ่งงานเป็นหน่วยย่อย (Sprints) ที่สามารถส่งมอบ "ซอฟต์แวร์ที่ใช้งานได้จริง" ในทุกรอบการทำงาน — เช่น Sprint แรกผู้ใช้ต้องสามารถ "จองห้องและดูรายการจองของตัวเองได้" แม้ยังไม่มีระบบอนุมัติ
- **Continuous Feedback:** ดึง Project Owner เข้ามามีส่วนร่วมในทุก Demo เพื่อให้มั่นใจว่าเรากำลังสร้างสิ่งที่ "ใช่" สำหรับผู้ใช้จริงๆ
- **Responding to Change:** พร้อมที่จะ Refactor หรือปรับปรุงส่วนสำคัญของระบบหากพบความต้องการใหม่ (เช่น ต้องเพิ่มระบบอนุมัติ 2 ชั้นกลาง Sprint)

---

### 8. Sprint Retrospective (การเรียนรู้จากอดีต)

ในทุกการสิ้นสุดรอบการทำงาน (Sprint) เราต้องมีการบันทึกสรุปเพื่อการพัฒนาทีมอย่างต่อเนื่อง:

- **Lessons Learned:** สิ่งที่ได้เรียนรู้ใหม่ๆ จากการพัฒนา
- **Technics:** เทคนิคการเขียนโค้ดหรือการใช้เครื่องมือที่พบว่ามีประสิทธิภาพ
- **Mistakes:** ข้อผิดพลาดที่เกิดขึ้นจริงเพื่อให้ทีมอื่นหรือตัวเองไม่ทำซ้ำ
- **Cautions:** ข้อควรระวังหรือความเสี่ยงที่อาจเกิดขึ้นในอนาคต

---

### 9. The Cockpit Principle (หน้าปัดเครื่องบิน)

เรายึดหลักการออกแบบ "ห้องนักบิน" เพื่อให้ผู้ดูแลระบบมีอำนาจการตัดสินใจบนพื้นฐานของข้อมูลที่ครบถ้วน (Data-Driven Decision):

- **Total Visibility (Know Everything):** Admin Dashboard ต้องแสดงสถานะห้องประชุมแบบ Real-time: ห้องไหนว่าง, ห้องไหนถูกจองแล้ว, อัตราการใช้ห้อง (Room Utilization), และการจองที่รอการอนุมัติ — เพื่อให้ตัดสินใจได้ก่อนจะเกิดปัญหา
- **Total Control (Control Everything):** ผู้ดูแลระบบต้องสามารถเปิด-ปิดห้อง, ปิดการจองในช่วงวันหยุด, หรือเปลี่ยนกฎการจอง (เช่น จำกัดระยะเวลาจองล่วงหน้า) ได้ทันทีผ่าน Admin Panel โดยไม่ต้อง Deploy โค้ดใหม่
- **Fail-Safe & Auditability:** ทุกการเปลี่ยนแปลง configuration ต้องมีการบันทึกร่องรอย (Logged) พร้อม Confirmation Dialog ป้องกันการกดผิด
- **Transparency over Obscurity:** ความซับซ้อนของระบบเบื้องหลังต้องถูกแปลงเป็นข้อมูลที่เข้าใจง่าย เช่น กราฟการใช้ห้องรายสัปดาห์ หรือ Top 5 ห้องที่ถูกจองบ่อยที่สุด

---

### 10. Booking UI Modularization — Config Isolated, Engine Shared

ระบบรองรับ Room Type และ Booking Form ที่หลากหลาย โดยยึดหลัก **"config แยก, engine ร่วม"**:

- **Config ต่อ room type** — แต่ละประเภทห้องมี config ของตัวเอง กำหนด field ที่ต้องกรอก, กฎการจอง (เช่น ต้องอนุมัติหรือไม่), และ equipment checklist โดยไม่กระทบประเภทอื่น
- **Booking Engine ร่วมกัน** — `BookingEngine` อ่าน config → render Booking Form → process การจองผ่าน engine เดียว
- **Component sharing** — shared components (RoomCalendar, TimeSlotPicker, AttendeeSelector, BookingSummary) ใช้ร่วมกันได้ทุก room type; room-specific components isolate อยู่ใน folder ของตัวเอง
- **Gate rule:** ห้าม hardcode Booking Flow สำหรับห้องที่ 3 ขึ้นไป — ต้องผ่าน Booking Engine เสมอ

> เพิ่ม Room Type ใหม่ = เพิ่ม config + component เดียว ไม่แตะ engine core

---

### 11. Component Communication Architecture (SE Perspective)

> *"A component that knows too much about its environment is a component that cannot be moved."*

ระบบ Booking Form ที่ดีทำงานเหมือนวงจรไฟฟ้า — กระแสไหลทิศทางเดียว ทุก node รู้หน้าที่ตัวเอง และไม่มี node ไหนที่ต้องรู้จักทุกอย่างในระบบ

#### 11.1 ลำดับชั้นการสื่อสาร (Communication Hierarchy)

```
┌─────────────────────────────────────────────────────┐
│  Level 1: Component ↔ Component                     │
│           props (ลงล่าง) + events/emit (ขึ้นบน)    │
│           Pattern: v-model (modelValue + update:)   │
├─────────────────────────────────────────────────────┤
│  Level 2: Component ↔ Application State             │
│           Pinia Store (reactive, centralized)       │
│           เฉพาะ Page/View layer เท่านั้น            │
├─────────────────────────────────────────────────────┤
│  Level 3: Application State ↔ Backend               │
│           Service Layer (bookingService, roomService│
│           authService) — Store เรียก Service เสมอ  │
├─────────────────────────────────────────────────────┤
│  ❌ FORBIDDEN: Component → API โดยตรง               │
│     Component ต้อง emit event ขึ้นไปให้ Store/Page  │
└─────────────────────────────────────────────────────┘
```

#### 11.2 Pure vs Smart Component — เลือกอย่างมีสติ

**Pure Component** (props in → events out):
```vue
<!-- ✅ ทดสอบง่าย ใช้ซ้ำได้ทุกที่ ไม่ผูกกับ store -->
<TimeSlotPicker :model-value="booking.timeSlot" @update:model-value="booking.updateTimeSlot" />
```
- ใช้กับ: TimeSlotPicker, RoomCard, AttendeeInput, DateRangePicker
- เกณฑ์: Component นี้อาจถูกใช้ใน context อื่น (เช่น modal แก้ไขการจอง) หรือไม่?
- ถ้าใช่ → ต้องเป็น Pure

**Smart Component** (อ่าน Store โดยตรง):
```vue
<!-- ✅ ยอมรับได้ เมื่อ component ต้องรวมข้อมูลจากหลาย sources -->
<!-- BookingSummary อ่าน roomStore + bookingStore เพื่อแสดงสรุปก่อนยืนยัน -->
```
- ใช้กับ: Orchestration components ที่ต้องการข้อมูลจากหลาย stores
- เกณฑ์: Component นี้จะไม่มีวันถูกนำไปใช้นอก Booking Flow นี้หรือไม่?
- ถ้าใช่ → Smart Component ยอมรับได้ แต่ต้องบันทึกไว้

**กฎเหล็ก:** Smart Component อ่าน Store ได้ แต่ต้องไม่เรียก API โดยตรง

#### 11.3 The Service Layer Contract — เส้นที่ต้องไม่ข้าม

```
❌ Component เรียก api.post('/bookings/...') โดยตรง
✅ Component emit('confirm', bookingData) → Store เรียก bookingService.create(bookingData)
```

เหตุผล:
1. **Error handling** — Store กำหนด error state กลาง Component ไม่ต้องจัดการ network error
2. **Loading state** — Store บอก UI ว่า "กำลังโหลด" ได้ทุก component พร้อมกัน
3. **Conflict handling** — ใส่ logic "ห้องถูกจองไปแล้ว" ใน service layer ครั้งเดียว ใช้ได้ทุกที่
4. **Testability** — Mock service ใน unit test แทนที่จะ mock axios

#### 11.4 The Snapshot Principle ในบริบท Booking

เมื่อผู้ใช้กดปุ่ม "ยืนยันการจอง" ข้อมูลต้องถูก freeze ณ จุดนั้น:

```typescript
// ❌ เก็บแค่ reference — ข้อมูลเปลี่ยนได้ในภายหลัง
booking.room_id = selectedRoom.id
booking.user_id = currentUser.id

// ✅ Snapshot — ข้อมูลตรึงอยู่กับการจองตลอดไป
booking.snapshot = {
  room_name: selectedRoom.name,
  room_capacity: selectedRoom.capacity,
  room_location: selectedRoom.location,
  booker_name: currentUser.full_name,
  booker_department: currentUser.department,
  booker_email: currentUser.email,
  confirmed_at: new Date().toISOString()
}
```

สำคัญเพราะ: หากห้องถูกเปลี่ยนชื่อหรือผู้ใช้ถูกย้ายหน่วยงานในภายหลัง ข้อมูลในประวัติการจองต้องยังคงสะท้อนความเป็นจริง ณ เวลาที่จอง

#### 11.5 Anti-Patterns ที่พบบ่อยใน Booking Systems

| Anti-Pattern | อาการ | วิธีแก้ |
|---|---|---|
| **God Component** | Component เดียวทำทุกอย่าง — เลือกห้อง, เลือกเวลา, validate, save, navigate | แยก responsibility ออกเป็น child components |
| **Prop Drilling** | ส่ง booking data ผ่าน 4-5 ชั้นเพื่อให้ถึง grandchild | ใช้ Pinia store หรือ provide/inject |
| **Direct API Call** | Component เรียก `axios.post('/bookings')` โดยตรง | ย้ายไป Service layer, component emit event |
| **Mutable Props** | Child แก้ไข prop โดยตรง (`props.booking.title = ...`) | ใช้ emit + v-model pattern เสมอ |
| **Store Bloat** | Store เก็บ UI state (modal open/close, selected tab) | UI state อยู่ใน component local ref เท่านั้น |

#### 11.6 Backend Service Layer Anti-Patterns

| Anti-Pattern | อาการ | วิธีแก้ |
|---|---|---|
| **Fat Router** | Router มี business logic (ตรวจสอบ conflict, คำนวณราคา) โดยตรง | ย้าย logic ทั้งหมดไป Service layer, router เหลือแค่ auth + schema validation |
| **No Conflict Check** | สร้าง Booking โดยไม่ lock row ก่อน → การจองซ้อนกัน | ใช้ `SELECT ... FOR UPDATE` หรือ Optimistic Locking ใน booking service |
| **Implicit Lazy Load** | Access `booking.room.equipment` หลัง async session ปิดแล้ว → `MissingGreenlet` | ใช้ `selectinload()` หรือ `joinedload()` ใน query เสมอเมื่อ relationship ถูกใช้ |
| **Raw Dict as User** | ใช้ `current_user["id"]` บางที่ + `current_user.id` อีกที่ | กำหนด `CurrentUser` TypedDict หรือ Pydantic model ครั้งเดียว ใช้ทั้ง codebase |
| **Hardcoded Path** | `"data/uploads/..."` ในโค้ด | ใช้ `settings.UPLOAD_DIR` จาก config เสมอ |
| **Unauthenticated Admin Route** | `/admin/rooms`, `/admin/reports` เปิดโล่ง | ทุก admin route ต้องมี `Depends(require_role("admin"))` — ไม่มีข้อยกเว้น |

---

### 12. Testing Philosophy — Integration Over Isolation

> *"A test that passes on mocks but fails in production has negative value — it gives false confidence."*

ระบบจองห้องประชุมที่มี Conflict Check และ Time Slot logic ต้องการ integration test เป็นหลัก:

- **ไม่ mock Database** — ทุก test ที่เกี่ยวกับ booking conflict ต้องใช้ SQLite in-memory จริง เหตุผล: Conflict Check ที่ถูกต้องอาศัย Database isolation level — mock จะ pass ทั้งหมดแต่ production จะ fail
- **Fresh DB ต่อ test** — แต่ละ test case ได้ DB สะอาด ป้องกัน state contamination ระหว่าง tests
- **Mock ได้เฉพาะ external services** — Email, LINE Notify, Calendar Sync (Google Calendar) — สิ่งที่ไม่มีใน dev environment จริง
- **Unit test เหมาะกับ Pure Functions** — `is_time_slot_available()`, Zod schemas, validation logic ที่ไม่มี side effect
- **ลำดับความสำคัญ:** Integration tests (DB + API) > Unit tests (pure logic) > E2E tests (UAT)

---

### 13. Documentation Drives Code — เอกสารนำทางโค้ดเสมอ

> *"Code without documentation is a decision without reasoning. Future developers — including yourself — deserve to know the why, not just the what."*

**กฎเหล็กของ P6BookingMe:** เอกสารต้องเสร็จก่อน โค้ดจึงเริ่มได้

#### ลำดับที่ต้องทำทุก Sprint ทุกครั้ง ไม่มีข้อยกเว้น

```
1. เขียน Sprint Doc (*.md ใน doc/bible_cluade_version/sprint_XX/)
   └─ เป้าหมาย, scope, definition of done, design decisions
        ↓
2. breakdown เป็น Tasks (TodoWrite)
        ↓
3. เขียนโค้ด (อ้างอิง Sprint Doc ตลอด)
        ↓
4. อัปเดต Roadmap (11_roadmap.md)
```

#### ทำไมต้องทำก่อนโค้ด

| ถ้าไม่มีเอกสาร | ผลที่เกิด |
|---|---|
| ไม่รู้ว่า scope จบที่ไหน | โค้ดขยายเกินกำหนด (scope creep) |
| ไม่บันทึก design decision | Sprint ถัดไปตัดสินใจซ้ำ (ซึ่งอาจผิดพลาดเหมือนเดิม) |
| ไม่มี definition of done | ไม่รู้ว่า "เสร็จ" หมายความว่าอะไร |
| ไม่มี context ใน doc | Claude ต้อง read codebase ใหม่ทุกครั้ง (เสียเวลา) |

#### เอกสาร = Memory ของโปรเจกต์

- **Sprint Doc** — บันทึก what + why + decisions ของแต่ละ sprint
- **Philosophy (ไฟล์นี้)** — หลักการที่ไม่เปลี่ยนแปลง กำกับทุกการตัดสินใจ
- **Roadmap** — ภาพรวม progress และ backlog ที่เป็น single source of truth
- **ADR (Architecture Decision Records)** — บันทึกการตัดสินใจสำคัญที่ส่งผลระยะยาว

#### กฎปฏิบัติ

- ถ้า Claude เสนอว่าจะ "เริ่มโค้ดเลย" — ให้หยุดและถามว่า "Sprint Doc เสร็จหรือยัง?"
- ถ้า feature ไม่มีใน Sprint Doc — ไม่ implement จนกว่าจะ document ก่อน
- Design decision ที่เกิดระหว้าง coding ต้องบันทึกย้อนหลังใน Sprint Doc ทันที

---

### 14. Software UI Designer World-Class Grade

เพื่อให้ระบบ **P6BookingMe** ก้าวสู่การเป็นซอฟต์แวร์ระดับสากล (World-Class) เรายึดถือหลักการออกแบบ UI/UX ที่ลึกซึ้งและสม่ำเสมอ ดังนี้:

#### 14.1 3 เสาหลักแห่งความเหนือระดับ (The 3 Pillars)
1. **Actor-Centric Use Cases:** ออกแบบตามบทบาทของผู้ใช้จริง (Member, Admin, Approver) เพื่อลด Cognitive Load และตอบโจทย์ Use Case เฉพาะทางของแต่ละกลุ่ม
2. **Premium UX/UI Excellence:** สร้างประสบการณ์ที่ "พรีเมียม" ผ่านการจัดวางข้อมูลที่สมเหตุสมผล (Information Hierarchy) และการใช้ Micro-interactions (Transitions/Hover) ที่นุ่มนวล
3. **Global UI Consistency:** ความสม่ำเสมอคือหัวใจหลัก ทุกหน้าจอต้องมี Interaction และ Visual Language ที่เป็นหนึ่งเดียว (เช่น คลิกแถว = ดูรายละเอียด เสมอ)

#### 14.2 Long Modal Architecture
สำหรับการแสดงรายละเอียดเชิงลึก (Drill-down) เรายึดหลัก **Long Modal Architecture** เป็นมาตรฐานหลักเพื่อสร้างประสบการณ์ระดับ World-Class:
- **Vertical Storytelling:** เลื่อนลงเพื่ออ่านเรื่องราวจากบนลงล่างอย่างลื่นไหล (เช่น ข้อมูลพื้นฐาน → ตารางเวลาวันนี้ → ประวัติย้อนหลัง)
- **Comprehensive Single-View:** แสดงข้อมูลครบถ้วนในหน้าเดียว ลดภาระการจำ (Cognitive Load) และลดจำนวนคลิกที่ผู้ใช้ต้องเปลี่ยน Tabs ไปมา
- **Standardized Depth:** ไม่ว่าจะเป็นข้อมูลประเภทใด หากมีการ Drill-down ต้องให้ความรู้สึกที่สม่ำเสมอตลอดทั้งแอปพลิเคชัน

#### 14.3 DaisyUI Integrity & Visual Balance
เราเคารพในงานออกแบบของ Framework หลักที่เราเลือกใช้:
- **Component Preservation:** ไม่ปรับแต่ง `round border` (border-radius) ของคอมโพเนนต์มาตรฐานจาก DaisyUI (เช่น Button, Badge, Card) หากไม่จำเป็นอย่างยิ่ง เนื่องจากทีมออกแบบได้ขัดเกลาความโค้งมนมาอย่างดีแล้ว
- **Standard over Custom:** ใช้ Utility classes มาตรฐานของ Tailwind/DaisyUI แทนการระบุค่าพิกเซลแบบ Hardcode (เช่น ใช้ `rounded-box` หรือ `rounded-2xl` แทน `rounded-[40px]`) เพื่อความสวยงามที่สอดคล้องกันทั้งระบบ

#### 14.4 View vs Edit Separation
ในระดับ Enterprise ต้องมีการแยกแยะสถานะการทำงานให้ชัดเจน:
- **View Mode:** ใช้ Modal เพื่อแสดงข้อมูลแบบ Read-only และประวัติการใช้งาน (History) เพื่อความปลอดภัย
- **Edit Mode:** ใช้หน้าจอแยกหรือ Form ที่ชัดเจน เพื่อป้องกันความผิดพลาดจากการแก้ไขข้อมูลโดยไม่ตั้งใจ (Accidental Data Modification)

---

> *"Architecture is the decisions that you wish you could get right early in a project."*  
> ด้วยหลักการเหล่านี้ เรากำลังตัดสินใจเพื่ออนาคตของ **P6BookingMe** — ระบบจองห้องประชุมที่สามารถขยาย บำรุงรักษา และส่งต่อได้โดยไม่ต้องอธิบายตั้งแต่ต้น