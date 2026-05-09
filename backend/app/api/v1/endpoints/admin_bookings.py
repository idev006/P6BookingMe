from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.models.booking import Booking, BookingStatus
from app.schemas.booking import BookingResponse
from app.schemas.common import StandardResponse
from app.services.audit import AuditService
from sqlalchemy import select, desc
import json

router = APIRouter()

@router.get("/", response_model=StandardResponse)
async def list_all_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    status: str | None = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import func, or_
    
    stmt = select(Booking)
    count_stmt = select(func.count()).select_from(Booking)
    
    # Filtering
    if status and status != 'all':
        stmt = stmt.where(Booking.status == status)
        count_stmt = count_stmt.where(Booking.status == status)
    
    if search:
        q = f"%{search}%"
        search_filter = or_(
            Booking.title.ilike(q),
            Booking.snap_user_name.ilike(q),
            Booking.snap_room_name.ilike(q)
        )
        stmt = stmt.where(search_filter)
        count_stmt = count_stmt.where(search_filter)
        
    total = await db.scalar(count_stmt)
    
    stmt = stmt.order_by(desc(Booking.created_at)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    bookings = result.scalars().all()
    
    return StandardResponse(data={
        "data": [BookingResponse.model_validate(b) for b in bookings],
        "total": total
    })

@router.post("/{booking_id}/cancel/", response_model=StandardResponse)
async def admin_cancel_booking(
    booking_id: int,
    reason: str = Body(..., embed=True),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    booking = await db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status in [BookingStatus.CANCELLED, BookingStatus.REJECTED]:
        raise HTTPException(status_code=400, detail="Cannot cancel an already finished booking")
    
    old_status = booking.status
    booking.status = BookingStatus.CANCELLED
    db.add(booking)
    await db.commit()
    
    # Audit Log
    audit = AuditService(db)
    await audit.log_action(
        user_id=current_user.id,
        action="admin.cancel_booking",
        resource_type="booking",
        resource_id=booking_id,
        old_value=old_status,
        new_value="cancelled",
        reason=reason
    )
    
    return StandardResponse(message=f"ยกเลิกการจองเรียบร้อยแล้ว (เหตุผล: {reason})")
