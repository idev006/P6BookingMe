import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.abspath("backend"))

from app.core.database import AsyncSessionLocal
from app.services.booking import BookingService
from app.models.user import User
from app.schemas.booking import BookingCreate

async def verify_business_rules():
    async with AsyncSessionLocal() as db:
        service = BookingService(db)
        
        # Mock admin user for test
        user = User(id=1, full_name="Admin Test", email="admin@example.com", role="admin")
        
        print("--- Testing BR-04: Max Duration (e.g. 10 hours) ---")
        try:
            now = datetime.now()
            data = BookingCreate(
                room_id=1,
                title="Long Meeting",
                start_time=now + timedelta(hours=1),
                end_time=now + timedelta(hours=11), # 10 hours
                attendee_count=5
            )
            await service.create_booking(user, data)
        except Exception as e:
            print(f"Caught expected error: {e.detail}")

        print("\n--- Testing BR-03: Max Advance Days (e.g. 100 days) ---")
        try:
            data = BookingCreate(
                room_id=1,
                title="Future Meeting",
                start_time=datetime.now() + timedelta(days=100),
                end_time=datetime.now() + timedelta(days=100, hours=1),
                attendee_count=5
            )
            await service.create_booking(user, data)
        except Exception as e:
            print(f"Caught expected error: {e.detail}")

if __name__ == "__main__":
    asyncio.run(verify_business_rules())
