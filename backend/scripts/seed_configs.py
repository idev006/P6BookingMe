import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.system_config import SystemConfig
from app.core.config import settings

async def seed_configs():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        configs = [
            {
                "config_key": "ENABLE_CONFLICT_CHECK",
                "config_value": True,
                "config_type": "bool",
                "description": "เปิด/ปิด การตรวจสอบการจองซ้อน",
                "category": "booking"
            },
            {
                "config_key": "ALLOW_PAST_BOOKING",
                "config_value": False,
                "config_type": "bool",
                "description": "อนุญาตให้จองเวลาย้อนหลังได้ (ไม่แนะนำสำหรับ Production)",
                "category": "booking"
            },
            {
                "config_key": "MIN_BOOKING_DURATION_MINS",
                "config_value": 30,
                "config_type": "int",
                "description": "ระยะเวลาจองขั้นต่ำ (นาที)",
                "category": "booking"
            },
            {
                "config_key": "MAX_BOOKING_DURATION_MINS",
                "config_value": 240,
                "config_type": "int",
                "description": "ระยะเวลาจองสูงสุดต่อครั้ง (นาที)",
                "category": "booking"
            },
            {
                "config_key": "MAINTENANCE_MODE",
                "config_value": False,
                "config_type": "bool",
                "description": "เปิดโหมดบำรุงรักษา (ปิดการจองชั่วคราว)",
                "category": "general"
            }
        ]

        for c_data in configs:
            config = SystemConfig(**c_data)
            session.add(config)
        
        try:
            await session.commit()
            print("Successfully seeded initial system configurations.")
        except Exception as e:
            print(f"Error seeding configs: {e}")

if __name__ == "__main__":
    asyncio.run(seed_configs())
