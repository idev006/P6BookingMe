from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification

class NotificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, notification: Notification) -> Notification:
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def get_multi_by_user(
        self, user_id: int, skip: int = 0, limit: int = 20, is_read: bool | None = None
    ) -> list[Notification]:
        query = select(Notification).where(Notification.user_id == user_id)
        if is_read is not None:
            query = query.where(Notification.is_read == is_read)
        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_user(self, user_id: int, is_read: bool | None = None) -> int:
        from sqlalchemy import func
        query = select(func.count()).select_from(Notification).where(Notification.user_id == user_id)
        if is_read is not None:
            query = query.where(Notification.is_read == is_read)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        query = update(Notification).where(
            Notification.id == notification_id, 
            Notification.user_id == user_id
        ).values(is_read=True)
        await self.session.execute(query)
        await self.session.commit()
        return True

    async def mark_all_as_read(self, user_id: int) -> int:
        query = update(Notification).where(
            Notification.user_id == user_id, 
            Notification.is_read == False
        ).values(is_read=True)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount
