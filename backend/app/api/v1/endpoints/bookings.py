from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingResponse, BookingListResponse, BookingReschedule, BookingUpdate
from app.services.booking import BookingService
from app.schemas.common import StandardResponse

router = APIRouter()

@router.post("/", response_model=StandardResponse)
async def create_booking(
    body: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BookingService(db)
    booking = await service.create_booking(current_user, body)
    return StandardResponse(
        data=BookingResponse.from_orm(booking),
        message="ส่งคำขอจองห้องประชุมเรียบร้อยแล้ว"
    )

@router.get("/", response_model=StandardResponse)
async def list_my_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query(None),
    status: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BookingService(db)
    bookings, total = await service.get_my_bookings(current_user.id, skip, limit, search, status)
    return StandardResponse(
        data={
            "total": total,
            "data": [BookingResponse.from_orm(b) for b in bookings]
        }
    )

@router.get("/{booking_id}", response_model=StandardResponse)
async def get_booking_detail(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BookingService(db)
    booking = await service.get_booking_detail(booking_id, current_user)
    return StandardResponse(
        data=BookingResponse.from_orm(booking)
    )

@router.post("/{booking_id}/cancel/", response_model=StandardResponse)
async def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BookingService(db)
    await service.cancel_booking(booking_id, current_user)
    return StandardResponse(
        message="ยกเลิกการจองเรียบร้อยแล้ว"
    )



@router.patch("/{booking_id}/reschedule/", response_model=StandardResponse)
async def reschedule_booking(
    booking_id: int,
    body: BookingReschedule,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BookingService(db)
    booking = await service.reschedule_booking(booking_id, current_user, body.start_time, body.end_time)
    return StandardResponse(
        data=BookingResponse.from_orm(booking),
        message="ปรับเปลี่ยนตารางการจองเรียบร้อยแล้ว"
    )

@router.patch("/{booking_id}", response_model=StandardResponse)
async def update_booking(
    booking_id: int,
    body: BookingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BookingService(db)
    booking = await service.update_booking(booking_id, current_user, body)
    return StandardResponse(
        data=BookingResponse.from_orm(booking),
        message="แก้ไขข้อมูลการจองเรียบร้อยแล้ว"
    )

@router.post("/{booking_id}/duplicate/", response_model=StandardResponse)
async def duplicate_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = BookingService(db)
    booking = await service.duplicate_booking(booking_id, current_user)
    return StandardResponse(
        data=BookingResponse.from_orm(booking),
        message="ดึงข้อมูลการจองเดิมเรียบร้อยแล้ว"
    )
