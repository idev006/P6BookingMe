import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from app.core.database import AsyncSessionLocal
from app.models.booking import Booking
from app.models.user import User
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Booking))
        bookings = res.scalars().all()
        print(f"Bookings count: {len(bookings)}")
        
        res = await db.execute(select(User))
        users = res.scalars().all()
        print(f"Users count: {len(users)}")
        for u in users:
            print(f" - {u.email} ({u.role})")

if __name__ == "__main__":
    asyncio.run(check())
