# 🏗️ P6BookingMe System Architecture (UML)

หน้านี้บรรจุแผนผัง UML เพื่อช่วยในการทำความเข้าใจโครงสร้างระบบและการ Debug

## 1. Package Diagram (System Layout)
แสดงโครงสร้างโฟลเดอร์และความสัมพันธ์ของแต่ละ Layer (4-Layer Architecture)

```mermaid
graph TD
    subgraph "Client Layer"
        Vue[Vue 3 Frontend]
    end

    subgraph "API Layer (FastAPI)"
        Endpoints[V1 Endpoints]
        Deps[Dependencies/Auth]
        Middleware[Traceability/Log]
    end

    subgraph "Business Logic Layer"
        Services[Services]
        Events[Event Manager/Handlers]
    end

    subgraph "Data Access Layer"
        Repos[Repositories]
        Models[SQLAlchemy Models]
    end

    subgraph "Core & Infrastructure"
        Config[Config/Env]
        DB[Database Session]
    end

    Vue --> Endpoints
    Endpoints --> Deps
    Endpoints --> Services
    Services --> Repos
    Services --> Events
    Repos --> Models
    Deps --> Repos
    Endpoints --> Middleware
    Middleware --> Config
    Services --> Config
```

---

## 2. Class Diagram (Core Models)
แสดงความสัมพันธ์ระหว่างข้อมูลหลักในระบบ เพื่อช่วยในการไล่ Logic ของ Database

```mermaid
classDiagram
    class User {
        +int id
        +string email
        +string employee_code
        +UserRole role
        +UserStatus status
        +anonymize()
    }

    class Room {
        +int id
        +string name
        +int capacity
        +RoomStatus status
        +invalidate_cache()
    }

    class Booking {
        +int id
        +int user_id
        +int room_id
        +datetime start_time
        +datetime end_time
        +BookingStatus status
        +json room_snapshot
        +check_in()
    }

    class Notification {
        +int id
        +int user_id
        +string title
        +bool is_read
    }

    class AuditLog {
        +int id
        +int user_id
        +string action
        +string target_type
        +json old_value
        +json new_value
    }

    User "1" --* "many" Booking : makes
    Room "1" --* "many" Booking : hosts
    User "1" --* "many" Notification : receives
    User "1" --* "many" AuditLog : performs
    Room "1" --* "many" RoomImage : has
    Room "1" --* "many" RoomEquipment : contains
    Booking "1" -- "1" User : approved_by
```

## 💡 ประโยชน์ในการ Debug:
1. **Circular Import Check**: หากมีการลากเส้นวนกลับใน Package Diagram ให้สงสัยว่าอาจเกิดปัญหา Circular Import
2. **Orphaned Data**: ช่วยให้เห็นความสัมพันธ์เพื่อตั้งค่า Cascade Delete ได้ถูกต้อง
3. **Event Trace**: อธิบายการไหลของข้อมูลจาก Service ไปยัง Event Handler โดยไม่ต้องผ่าน API โดยตรง
