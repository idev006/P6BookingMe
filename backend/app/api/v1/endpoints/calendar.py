from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user, require_admin
from app.models.user import User
from app.models.booking import Booking, BookingStatus, BookingApproval
from app.schemas.booking import BookingResponse
from app.schemas.common import StandardResponse
from sqlalchemy import select, and_
from datetime import datetime
from typing import List, Optional

router = APIRouter()

@router.get("/", response_model=StandardResponse)
async def get_calendar_bookings(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    room_id: Optional[int] = Query(None),
    building: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Fetch all bookings for calendar view within a date range."""
    from app.models.room import Room
    
    query = and_(
        Booking.start_time >= start_date,
        Booking.end_time <= end_date
    )
    
    if room_id:
        query = and_(query, Booking.room_id == room_id)
    if status:
        query = and_(query, Booking.status == status)
    else:
        # Default: show active bookings
        query = and_(query, Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]))
        
    from sqlalchemy.orm import selectinload
    stmt = (
        select(Booking)
        .where(query)
        .options(
            selectinload(Booking.approval).selectinload(BookingApproval.approver)
        )
    )
    
    # Join with Room if building filter is provided
    if building:
        stmt = stmt.join(Room, Booking.room_id == Room.id).where(Room.building == building)
        
    result = await db.execute(stmt)
    bookings = result.scalars().all()
    
    response_data = []
    for b in bookings:
        res = BookingResponse.model_validate(b)
        if b.approval:
            res.approved_by_name = b.approval.approver.full_name
            res.approval_note = b.approval.reason
            res.approved_at = b.approval.actioned_at
        response_data.append(res)
        
    return StandardResponse(data=response_data)


@router.post("/maintenance", response_model=StandardResponse)
async def add_maintenance(
    body: dict,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Admin only: Block a room for maintenance."""
    from app.models.room import Room
    room = await db.get(Room, body['room_id'])
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    booking = Booking(
        user_id=current_user.id,
        room_id=room.id,
        title=body['title'],
        start_time=datetime.fromisoformat(body['start_time'].replace('Z', '')),
        end_time=datetime.fromisoformat(body['end_time'].replace('Z', '')),
        status=BookingStatus.MAINTENANCE,
        # Snapshots
        snap_room_name=room.name,
        snap_room_capacity=room.capacity,
        snap_room_location=room.location,
        snap_user_name=current_user.full_name,
        snap_user_department=current_user.department or "Admin",
        snap_user_email=current_user.email
    )
    db.add(booking)
    await db.commit()
    return StandardResponse(message="บันทึกตารางการบำรุงรักษาเรียบร้อยแล้ว")
