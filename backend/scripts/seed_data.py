import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.room import Room, RoomImage, RoomEquipment, RoomStatus
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from sqlalchemy import select
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_data():
    logger.info("Seeding dummy data...")
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as db:
        # 0. Get Admin User
        admin_res = await db.execute(select(User).where(User.email == "admin@p6bookingme.com"))
        admin = admin_res.scalars().first()
        if not admin:
            logger.error("Admin user not found. Please run create_admin.py first.")
            return

        # 1. Create Rooms
        rooms_data = [
            {
                "name": "Grand Ballroom",
                "capacity": 100,
                "location": "อาคาร A ชั้น 1",
                "building": "อาคาร A",
                "floor": "1",
                "description": "ห้องประชุมขนาดใหญ่ เหมาะสำหรับงานสัมมนาหรืองานเลี้ยงบริษัท พร้อมระบบเสียงสเตอริโอ",
                "status": RoomStatus.ACTIVE
            },
            {
                "name": "Creative Studio",
                "capacity": 12,
                "location": "อาคาร B ชั้น 3",
                "building": "อาคาร B",
                "floor": "3",
                "description": "ห้องประชุมสไตล์โมเดิร์น กระตุ้นความคิดสร้างสรรค์ พร้อมกระดานไวท์บอร์ดกระจก",
                "status": RoomStatus.ACTIVE
            }
        ]
        
        for r_data in rooms_data:
            result = await db.execute(select(Room).where(Room.name == r_data["name"]))
            room = result.scalars().first()
            if not room:
                room = Room(**r_data)
                db.add(room)
                await db.flush()
                
                # Add Equipment
                for eq_name in ["Projector", "Wi-Fi High Speed"]:
                    db.add(RoomEquipment(room_id=room.id, name=eq_name))
                
                db.add(RoomImage(room_id=room.id, image_path="dummy_room.jpg", is_primary=True))
                logger.info(f"Added room: {r_data['name']}")

            # 2. Add Dummy Bookings for this room (for Admin)
            # Confirmed Booking
            booking1 = Booking(
                room_id=room.id,
                user_id=admin.id,
                title=f"ประชุม {r_data['name']} ประจำสัปดาห์",
                description="ประชุมติดตามงานส่วนกลาง",
                start_time=datetime.utcnow() + timedelta(days=1, hours=9),
                end_time=datetime.utcnow() + timedelta(days=1, hours=11),
                status=BookingStatus.CONFIRMED,
                snap_room_name=room.name,
                snap_room_capacity=room.capacity,
                snap_room_location=room.location,
                snap_user_name=admin.full_name,
                snap_user_department=admin.department,
                snap_user_email=admin.email,
                attendee_count=5
            )
            db.add(booking1)

            # Pending Booking
            booking2 = Booking(
                room_id=room.id,
                user_id=admin.id,
                title="Workshop ระดมสมอง",
                description="ทีมดีไซน์นัดคุยเรื่องโปรเจกต์ใหม่",
                start_time=datetime.utcnow() + timedelta(days=2, hours=14),
                end_time=datetime.utcnow() + timedelta(days=2, hours=16),
                status=BookingStatus.PENDING,
                snap_room_name=room.name,
                snap_room_capacity=room.capacity,
                snap_room_location=room.location,
                snap_user_name=admin.full_name,
                snap_user_department=admin.department,
                snap_user_email=admin.email,
                attendee_count=10
            )
            db.add(booking2)
        
        await db.commit()
    
    logger.info("Seeding completed.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_data())
