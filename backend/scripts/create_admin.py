import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.user import User, UserRole, UserStatus
from app.core.security import get_password_hash
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_admin():
    logger.info("Creating default admin user...")
    engine = create_async_engine(settings.DATABASE_URL)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with AsyncSessionLocal() as db:
        admin_email = "admin@p6bookingme.com"
        
        # Check if exists
        result = await db.execute(select(User).where(User.email == admin_email))
        existing = result.scalars().first()
        
        if not existing:
            admin = User(
                email=admin_email,
                password_hash=get_password_hash("admin1234"),
                employee_code="ADMIN001",
                full_name="System Administrator",
                department="IT",
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE
            )
            db.add(admin)
            await db.commit()
            logger.info(f"Admin user created: {admin_email}")
        else:
            logger.info("Admin user already exists.")
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_admin())
