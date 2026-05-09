import asyncio
import bcrypt
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole, UserStatus

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def seed_admin():
    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        result = await session.execute(select(User).where(User.email == "admin@booking.me"))
        admin = result.scalar_one_or_none()

        if admin:
            print("Admin user already exists!")
            return

        print("Creating admin user...")
        new_admin = User(
            email="admin@booking.me",
            password_hash=get_password_hash("AdminP@ssw0rd!"),
            employee_code="ADMIN001",
            full_name="System Administrator",
            department="IT",
            phone="0800000000",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        
        session.add(new_admin)
        await session.commit()
        print("Admin user created successfully: admin@booking.me / AdminP@ssw0rd!")

if __name__ == "__main__":
    asyncio.run(seed_admin())
