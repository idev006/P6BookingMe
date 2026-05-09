from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from app.models.notification import Notification, NotificationType
from typing import List

class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def notify_user(self, user_id: int, type: NotificationType, message: str, booking_id: int = None):
        notif = Notification(
            user_id=user_id,
            type=type,
            message=message,
            booking_id=booking_id
        )
        self.db.add(notif)
        await self.db.commit()
        return notif

    async def get_my_notifications(self, user_id: int, limit: int = 10) -> List[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id).order_by(desc(Notification.created_at)).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def mark_as_read(self, notification_id: int, user_id: int):
        stmt = update(Notification).where(
            Notification.id == notification_id, 
            Notification.user_id == user_id
        ).values(is_read=True)
        await self.db.execute(stmt)
        await self.db.commit()

    async def mark_all_as_read(self, user_id: int):
        stmt = update(Notification).where(
            Notification.user_id == user_id, 
            Notification.is_read == False
        ).values(is_read=True)
        await self.db.execute(stmt)
        await self.db.commit()
