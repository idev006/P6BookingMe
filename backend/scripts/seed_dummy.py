import asyncio
import random
from datetime import datetime, timedelta, UTC
from sqlalchemy import select
from faker import Faker

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal, engine
from app.models.user import User, UserRole, UserStatus
from app.models.room import Room, RoomStatus, RoomEquipment, RoomImage
from app.models.booking import Booking, BookingStatus, BookingApproval
from app.models.notification import Notification, NotificationType
from app.models.audit_log import AuditLog
from app.core.security import get_password_hash

fake = Faker(['th_TH', 'en_US'])

async def seed_data():
    async with AsyncSessionLocal() as db:
        print("Cleaning up existing data...")
        await db.execute(AuditLog.__table__.delete())
        await db.execute(Notification.__table__.delete())
        await db.execute(BookingApproval.__table__.delete())
        await db.execute(Booking.__table__.delete())
        await db.execute(RoomEquipment.__table__.delete())
        await db.execute(RoomImage.__table__.delete())
        await db.execute(Room.__table__.delete())
        await db.execute(User.__table__.delete())
        await db.commit()
        
        print("Starting massive seeding (1000+ records)...")
        
        # --- 1. Users (~100 users) ---
        password_hash = get_password_hash("password123")
        departments = ["IT", "HR", "Sales", "Marketing", "Finance", "Legal", "Operations", "R&D", "Customer Support"]
        
        # Primary test accounts
        admin = User(email="admin@p6booking.me", password_hash=password_hash, full_name="Admin System", employee_code="ADM001", department="IT", role=UserRole.ADMIN, status=UserStatus.ACTIVE)
        approver = User(email="approver@p6booking.me", password_hash=password_hash, full_name="Somchai Approver", employee_code="APP001", department="HR", role=UserRole.APPROVER, status=UserStatus.ACTIVE)
        member = User(email="member@p6booking.me", password_hash=password_hash, full_name="Somsak Member", employee_code="MEM001", department="Marketing", role=UserRole.MEMBER, status=UserStatus.ACTIVE)
        
        db.add_all([admin, approver, member])
        
        users = [admin, approver, member]
        for i in range(97):
            u = User(
                email=fake.unique.email(),
                password_hash=password_hash,
                full_name=fake.name(),
                employee_code=f"EMP{200+i}",
                department=random.choice(departments),
                role=random.choices([UserRole.MEMBER, UserRole.APPROVER], weights=[85, 15])[0],
                status=random.choices([UserStatus.ACTIVE, UserStatus.PENDING, UserStatus.REJECTED, UserStatus.SUSPENDED], weights=[80, 10, 5, 5])[0]
            )
            db.add(u)
            users.append(u)
        
        await db.flush()
        
        # --- 2. Rooms (~20 rooms) ---
        rooms = []
        buildings = ["Building A", "Building B", "Building C", "Building D", "Headquarters"]
        equipments_pool = ["Projector", "Whiteboard", "TV Screen", "Video Conference", "Sound System", "Coffee Machine", "High-speed Internet", "Flipchart", "Wireless Mic"]
        
        for i in range(20):
            b = random.choice(buildings)
            f_num = random.randint(1, 10)
            room = Room(
                name=f"{fake.word().capitalize()} Room {i+1}",
                location=f"{b}, Floor {f_num}",
                capacity=random.choice([4, 6, 8, 10, 12, 15, 20, 30, 50, 100]),
                building=b,
                floor=str(f_num),
                description=fake.sentence(nb_words=10),
                status=random.choices([RoomStatus.ACTIVE, RoomStatus.INACTIVE], weights=[90, 10])[0]
            )
            db.add(room)
            
            # Add 2-6 random equipment
            for eq_name in random.sample(equipments_pool, k=random.randint(2, 6)):
                db.add(RoomEquipment(room=room, name=eq_name))
                
            rooms.append(room)
            
        await db.flush()
        
        # --- 3. Bookings (~1000 bookings) ---
        now = datetime.now()
        active_users = [u for u in users if u.status == UserStatus.ACTIVE]
        approvers = [u for u in users if u.role in [UserRole.APPROVER, UserRole.ADMIN]]
        
        print(f"Generating 1000 bookings...")
        for i in range(1000):
            user = random.choice(active_users)
            room = random.choice(rooms)
            
            # Spread bookings over 6 months past and 2 months future
            days_offset = random.randint(-180, 60)
            start_hour = random.randint(8, 17)
            start_time = now.replace(hour=start_hour, minute=0, second=0, microsecond=0) + timedelta(days=days_offset)
            end_time = start_time + timedelta(hours=random.randint(1, 4))
            
            # Logic for status based on time
            if days_offset < -2: # Well in the past
                status = random.choices([BookingStatus.CONFIRMED, BookingStatus.REJECTED, BookingStatus.CANCELLED], weights=[70, 20, 10])[0]
            elif days_offset <= 0: # Recent
                status = random.choices([BookingStatus.PENDING, BookingStatus.CONFIRMED], weights=[40, 60])[0]
            else: # Future
                status = random.choices([BookingStatus.PENDING, BookingStatus.CONFIRMED], weights=[80, 20])[0]
                
            booking = Booking(
                room_id=room.id,
                user_id=user.id,
                title=f"Session: {fake.catch_phrase()}",
                description=fake.paragraph(nb_sentences=2),
                start_time=start_time,
                end_time=end_time,
                status=status,
                attendee_count=random.randint(2, room.capacity),
                snap_room_name=room.name,
                snap_room_location=room.location,
                snap_room_capacity=room.capacity,
                snap_user_name=user.full_name,
                snap_user_department=user.department,
                snap_user_email=user.email,
                created_at=start_time - timedelta(days=random.randint(1, 10))
            )
            db.add(booking)
            
            # Add Approval Record if not Pending
            if status in [BookingStatus.CONFIRMED, BookingStatus.REJECTED]:
                approver_user = random.choice(approvers)
                action = 'approved' if status == BookingStatus.CONFIRMED else 'rejected'
                approval = BookingApproval(
                    booking=booking,
                    approver_id=approver_user.id,
                    action=action,
                    reason=fake.sentence() if action == 'rejected' else None,
                    actioned_at=booking.created_at + timedelta(hours=random.randint(1, 24))
                )
                db.add(approval)
            
            if i % 200 == 0:
                print(f"  Progress: {i}/1000...")
                await db.flush()
                
        # --- 4. Notifications (~300 records) ---
        print("Generating notifications...")
        for i in range(300):
            target_user = random.choice(users)
            db.add(Notification(
                user_id=target_user.id,
                type=random.choice(list(NotificationType)),
                message=fake.sentence(),
                is_read=random.choice([True, False, False]), # More unread
                created_at=now - timedelta(days=random.randint(0, 30))
            ))
            
        # --- 5. Audit Logs (~500 records) ---
        print("Generating audit logs...")
        actions = ["user.login", "user.update", "booking.create", "booking.cancel", "room.create", "room.update", "config.update", "auth.logout"]
        for i in range(500):
            log_user = random.choice(users)
            db.add(AuditLog(
                user_id=log_user.id,
                action=random.choice(actions),
                entity_type=random.choice(["user", "booking", "room", "config", "system"]),
                entity_id=random.randint(1, 100),
                ip_address=fake.ipv4(),
                created_at=now - timedelta(days=random.randint(0, 60))
            ))
            
        await db.commit()
        print("SUCCESS: Massive seeding completed!")

if __name__ == "__main__":
    asyncio.run(seed_data())
