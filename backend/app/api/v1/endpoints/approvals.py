from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import require_approver
from app.models.user import User
from app.models.booking import Booking, BookingStatus, BookingApproval
from app.schemas.booking import BookingResponse
from app.schemas.common import StandardResponse
from sqlalchemy import select, desc
from typing import Optional

router = APIRouter()

@router.get("/summary", response_model=StandardResponse)
async def get_approvals_summary(
    current_user: User = Depends(require_approver),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import func
    
    # Count total pending in system
    pending_count_stmt = select(func.count()).select_from(Booking).where(Booking.status == BookingStatus.PENDING)
    pending_count = await db.scalar(pending_count_stmt)
    
    # Count my historical actions
    my_actions_count_stmt = select(func.count()).select_from(BookingApproval).where(BookingApproval.approver_id == current_user.id)
    my_actions_count = await db.scalar(my_actions_count_stmt)
    
    # Get last 5 actions for quick view
    stmt = select(BookingApproval).where(
        BookingApproval.approver_id == current_user.id
    ).order_by(desc(BookingApproval.actioned_at)).limit(5)
    
    result = await db.execute(stmt)
    recent_approvals = result.scalars().all()
    
    recent_data = []
    for app in recent_approvals:
        booking = await db.get(Booking, app.booking_id)
        recent_data.append({
            "id": app.id,
            "action": app.action,
            "actioned_at": app.actioned_at,
            "booking_title": booking.title if booking else "N/A"
        })

    return StandardResponse(data={
        "pending_count": pending_count,
        "my_actions_total": my_actions_count,
        "recent_actions": recent_data
    })

@router.get("/pending", response_model=StandardResponse)
async def list_pending_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_approver),
    db: AsyncSession = Depends(get_db)
):
    from app.services.booking import BookingService
    service = BookingService(db)
    bookings, total = await service.booking_repo.list_bookings(
        status=BookingStatus.PENDING,
        search=search,
        skip=skip,
        limit=limit
    )
    return StandardResponse(
        data={
            "total": total,
            "data": [BookingResponse.model_validate(b) for b in bookings]
        }
    )

@router.get("/history", response_model=StandardResponse)
async def list_my_approvals(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(require_approver),
    db: AsyncSession = Depends(get_db)
):
    """List bookings that I have approved or rejected."""
    stmt = select(BookingApproval).where(
        BookingApproval.approver_id == current_user.id
    ).order_by(desc(BookingApproval.actioned_at)).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    approvals = result.scalars().all()
    
    # We need to load the associated bookings too
    # For simplicity in this demo, I'll return the approval objects with some booking info
    data = []
    for app in approvals:
        booking = await db.get(Booking, app.booking_id)
        data.append({
            "id": app.id,
            "action": app.action,
            "reason": app.reason,
            "actioned_at": app.actioned_at,
            "booking": BookingResponse.model_validate(booking) if booking else None
        })
        
    from sqlalchemy import func
    count_stmt = select(func.count()).select_from(BookingApproval).where(BookingApproval.approver_id == current_user.id)
    total = await db.scalar(count_stmt)
    
    return StandardResponse(data={
        "data": data,
        "total": total
    })

@router.post("/{booking_id}/approve", response_model=StandardResponse)
async def approve_booking(
    booking_id: int,
    note: Optional[str] = Body(None, embed=True),
    current_user: User = Depends(require_approver),
    db: AsyncSession = Depends(get_db)
):
    from app.services.booking import BookingService
    service = BookingService(db)
    booking = await service.approve_booking(booking_id, current_user, note)
    return StandardResponse(data=BookingResponse.model_validate(booking), message="อนุมัติการจองเรียบร้อยแล้ว")

@router.post("/{booking_id}/reject", response_model=StandardResponse)
async def reject_booking(
    booking_id: int,
    note: str = Body(..., embed=True),
    current_user: User = Depends(require_approver),
    db: AsyncSession = Depends(get_db)
):
    from app.services.booking import BookingService
    service = BookingService(db)
    booking = await service.reject_booking(booking_id, current_user, note)
    return StandardResponse(data=BookingResponse.model_validate(booking), message="ปฏิเสธการจองเรียบร้อยแล้ว")
