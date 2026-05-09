from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from app.models.booking import Booking, BookingStatus
from datetime import datetime
from typing import List, Optional

class BookingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, booking: Booking) -> Booking:
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def get_by_id(self, booking_id: int) -> Optional[Booking]:
        stmt = (
            select(Booking)
            .where(Booking.id == booking_id)
            .options(selectinload(Booking.room), selectinload(Booking.user))
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def list_bookings(
        self, 
        user_id: Optional[int] = None, 
        room_id: Optional[int] = None,
        status: Optional[BookingStatus] = None,
        search: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> (List[Booking], int):
        from sqlalchemy import or_
        filters = []
        if user_id:
            filters.append(Booking.user_id == user_id)
        if room_id:
            filters.append(Booking.room_id == room_id)
        if status:
            filters.append(Booking.status == status)
        
        if search:
            q = f"%{search}%"
            filters.append(or_(
                Booking.title.ilike(q),
                Booking.snap_user_name.ilike(q),
                Booking.snap_room_name.ilike(q)
            ))

        # Count
        count_stmt = select(func.count()).select_from(Booking)
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total = await self.db.execute(count_stmt)
        total_count = total.scalar()

        # Data
        stmt = select(Booking).offset(skip).limit(limit).order_by(Booking.created_at.desc())
        if filters:
            stmt = stmt.where(and_(*filters))
        
        result = await self.db.execute(stmt)
        return result.scalars().all(), total_count

    async def update(self, booking: Booking) -> Booking:
        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def find_conflicts(self, room_id: int, start: datetime, end: datetime, exclude_id: Optional[int] = None) -> List[Booking]:
        """
        Finds any confirmed or pending bookings that overlap with the given time range.
        Uses with_for_update() to lock rows and prevent race conditions.
        """
        filters = [
            Booking.room_id == room_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            Booking.start_time < end,
            Booking.end_time > start
        ]
        
        if exclude_id:
            filters.append(Booking.id != exclude_id)
            
        stmt = (
            select(Booking)
            .where(and_(*filters))
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    async def count_user_bookings_for_date(self, user_id: int, date_val: datetime.date) -> int:
        """Counts non-cancelled bookings for a specific user on a specific date."""
        from sqlalchemy import cast, Date
        stmt = select(func.count()).select_from(Booking).where(
            and_(
                Booking.user_id == user_id,
                cast(Booking.start_time, Date) == date_val,
                Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
