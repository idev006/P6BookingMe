from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from app.models.booking import Booking, BookingStatus
from app.models.room import Room
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
import csv
import io

class ReportingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_summary_stats(self) -> Dict[str, Any]:
        """Summary of today's bookings and pending ones."""
        today = date.today()
        
        # Today's bookings
        stmt_today = select(func.count()).select_from(Booking).where(
            func.date(Booking.start_time) == today
        )
        # Pending bookings
        stmt_pending = select(func.count()).select_from(Booking).where(
            Booking.status == BookingStatus.PENDING
        )
        # Confirmed today
        stmt_confirmed = select(func.count()).select_from(Booking).where(
            and_(
                func.date(Booking.start_time) == today,
                Booking.status == BookingStatus.CONFIRMED
            )
        )

        today_count = (await self.db.execute(stmt_today)).scalar() or 0
        pending_count = (await self.db.execute(stmt_pending)).scalar() or 0
        confirmed_count = (await self.db.execute(stmt_confirmed)).scalar() or 0

        return {
            "today_total": today_count,
            "today_confirmed": confirmed_count,
            "pending_approval": pending_count
        }

    async def get_frequent_rooms(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Top rooms by booking count."""
        stmt = (
            select(
                Booking.snap_room_name.label("room_name"),
                func.count(Booking.id).label("count")
            )
            .group_by(Booking.snap_room_name)
            .order_by(desc("count"))
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return [{"name": r.room_name, "value": r.count} for r in result.all()]

    async def get_usage_trends(self, days: int = 7) -> List[Dict[str, Any]]:
        """Booking counts for the last N days."""
        start_date = date.today() - timedelta(days=days-1)
        
        # This is a bit tricky with SQLite date functions
        stmt = (
            select(
                func.date(Booking.start_time).label("date"),
                func.count(Booking.id).label("count")
            )
            .where(func.date(Booking.start_time) >= start_date)
            .group_by(func.date(Booking.start_time))
            .order_by("date")
        )
        result = await self.db.execute(stmt)
        data = {r.date: r.count for r in result.all()}
        
        # Fill gaps
        trends = []
        for i in range(days):
            d = (start_date + timedelta(days=i)).isoformat()
            trends.append({"date": d, "count": data.get(d, 0)})
            
        return trends

    async def export_bookings_csv(self, start_date: date = None, end_date: date = None) -> str:
        """Generates a CSV string for bookings."""
        stmt = select(Booking).order_by(Booking.start_time.desc())
        if start_date:
            stmt = stmt.where(func.date(Booking.start_time) >= start_date)
        if end_date:
            stmt = stmt.where(func.date(Booking.start_time) <= end_date)
            
        result = await self.db.execute(stmt)
        bookings = result.scalars().all()

        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            "ID", "Title", "Room", "Location", "User", "Dept", 
            "Start", "End", "Status", "Attendee Count"
        ])
        
        for b in bookings:
            writer.writerow([
                b.id, b.title, b.snap_room_name, b.snap_room_location,
                b.snap_user_name, b.snap_user_department,
                b.start_time.isoformat(), b.end_time.isoformat(),
                b.status, b.attendee_count
            ])
            
        return output.getvalue()
