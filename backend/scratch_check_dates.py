import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from app.core.database import AsyncSessionLocal
from app.models.booking import Booking
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Booking))
        bookings = res.scalars().all()
        invalid = []
        for b in bookings:
            if not b.start_time or not b.end_time:
                invalid.append(b.id)
        print(f"Invalid bookings count: {len(invalid)}")
        if len(bookings) > 0:
            print(f"Sample booking start_time: {bookings[0].start_time} (type: {type(bookings[0].start_time)})")

if __name__ == "__main__":
    asyncio.run(check())
