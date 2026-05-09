import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.system_config import SystemConfig
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_config():
    logger.info("Seeding system configurations...")
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as db:
        configs = [
            {
                "key": "GHOST_BOOKING_EXPIRE_MINS",
                "value": "30",
                "description": "เวลาที่จะยกเลิกการจองที่ค้างอยู่ในสถานะ Pending (นาที)"
            },
            {
                "key": "GHOST_CLEANUP_INTERVAL_MINS",
                "value": "10",
                "description": "ความถี่ในการรันระบบตรวจสอบการจองที่หมดอายุ (นาที)"
            },
            {
                "key": "max_advance_days",
                "value": "30",
                "description": "จองล่วงหน้าได้สูงสุด (วัน)"
            },
            {
                "key": "max_booking_hours",
                "value": "4",
                "description": "ระยะเวลาจองสูงสุดต่อครั้ง (ชั่วโมง)"
            }
        ]
        
        for cfg_data in configs:
            # Check if exists
            result = await db.execute(select(SystemConfig).where(SystemConfig.key == cfg_data["key"]))
            existing = result.scalars().first()
            
            if not existing:
                cfg = SystemConfig(**cfg_data)
                db.add(cfg)
                logger.info(f"Added config: {cfg_data['key']}")
        
        await db.commit()
    
    logger.info("Seeding completed.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_config())
