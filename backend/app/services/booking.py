from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.booking import Booking, BookingStatus, BookingApproval
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingUpdate
from app.repositories.booking import BookingRepository
from app.repositories.room import RoomRepository
from app.services.audit import AuditService
from app.services.config_service import ConfigService
from app.services.event_manager import event_manager
from datetime import datetime, timedelta
import json

class BookingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.booking_repo = BookingRepository(db)
        self.room_repo = RoomRepository(db)
        self.audit_service = AuditService(db)
        self.config_service = ConfigService(db)

    async def create_booking(self, user: User, data: BookingCreate) -> Booking:
        allow_past = await self.config_service.get_value("ALLOW_PAST_BOOKING", False)
        enable_conflict_check = await self.config_service.get_value("ENABLE_CONFLICT_CHECK", True)
        
        # 1. Validate Room
        room = await self.room_repo.get_by_id(data.room_id)
        if not room:
            raise HTTPException(status_code=404, detail="ไม่พบห้องประชุมที่ระบุ")
        if room.status != "active":
            raise HTTPException(status_code=400, detail="ห้องประชุมนี้ไม่เปิดให้บริการ")

        # 2. Basic Time Validation
        duration_hrs = (data.end_time - data.start_time).total_seconds() / 3600
        if data.start_time >= data.end_time:
            raise HTTPException(status_code=400, detail="เวลาสิ้นสุดต้องมากกว่าเวลาเริ่มต้น")
            
        if not allow_past and data.start_time < datetime.now():
            raise HTTPException(status_code=400, detail="ไม่สามารถจองเวลาย้อนหลังได้")

        # BR-04: Max Duration Check
        max_duration = await self.config_service.get_value("MAX_BOOKING_HOURS", 4)
        if duration_hrs > float(max_duration):
            raise HTTPException(status_code=400, detail=f"ระยะเวลาการจองสูงสุดต่อครั้งคือ {max_duration} ชั่วโมง")

        # BR-03: Max Advance Days
        max_advance = await self.config_service.get_value("MAX_ADVANCE_DAYS", 30)
        if (data.start_time - datetime.now()).days > int(max_advance):
            raise HTTPException(status_code=400, detail=f"สามารถจองล่วงหน้าได้ไม่เกิน {max_advance} วัน")

        # BR-02: Max Bookings Per Day
        max_per_day = await self.config_service.get_value("MAX_BOOKINGS_PER_DAY", 3)
        current_daily_count = await self.booking_repo.count_user_bookings_for_date(user.id, data.start_time.date())
        if current_daily_count >= int(max_per_day):
            raise HTTPException(status_code=400, detail=f"คุณจองห้องประชุมครบโควตา {max_per_day} ครั้งต่อวันแล้ว")

        # 3. Check for conflicts
        if enable_conflict_check:
            conflicts = await self.booking_repo.find_conflicts(data.room_id, data.start_time, data.end_time)
            if conflicts:
                raise HTTPException(
                    status_code=409, 
                    detail="ช่วงเวลาดังกล่าวถูกจองไปแล้ว กรุณาเลือกช่วงเวลาอื่น"
                )

        # 4. Create Booking with Snapshots (SSOT Compliance)
        booking = Booking(
            user_id=user.id,
            room_id=data.room_id,
            title=data.title,
            description=data.description,
            start_time=data.start_time,
            end_time=data.end_time,
            attendee_count=data.attendee_count,
            status=BookingStatus.PENDING,
            
            # Snapshots
            snap_room_name=room.name,
            snap_room_capacity=room.capacity,
            snap_room_location=room.location,
            snap_user_name=user.full_name,
            snap_user_department=user.department or "N/A",
            snap_user_email=user.email
        )

        new_booking = await self.booking_repo.create(booking)

        # Audit Log
        await self.audit_service.log_action(
            user_id=user.id,
            action="booking.create",
            resource_type="booking",
            resource_id=new_booking.id,
            new_value=json.dumps(data.model_dump(), default=str)
        )

        return new_booking

    async def get_my_bookings(self, user_id: int, skip: int = 0, limit: int = 20, search: str = None, status: str = None) -> (list[Booking], int):
        from app.models.booking import BookingStatus
        booking_status = None
        if status and status != 'all':
            try:
                booking_status = BookingStatus(status)
            except ValueError:
                pass
        return await self.booking_repo.list_bookings(user_id=user_id, skip=skip, limit=limit, search=search, status=booking_status)

    async def cancel_booking(self, booking_id: int, user: User, reason: str = None) -> Booking:
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลการจอง")
        
        if booking.user_id != user.id and user.role != "admin":
            raise HTTPException(status_code=403, detail="คุณไม่มีสิทธิ์ยกเลิกการจองนี้")
        
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.REJECTED]:
            raise HTTPException(status_code=400, detail=f"ไม่สามารถยกเลิกการจองที่มีสถานะ {booking.status} ได้")

        old_status = booking.status
        booking.status = BookingStatus.CANCELLED
        booking.cancel_reason = reason
        booking.cancelled_by = user.id
        
        updated_booking = await self.booking_repo.update(booking)

        # Audit Log
        await self.audit_service.log_action(
            user_id=user.id,
            action="booking.cancel",
            resource_type="booking",
            resource_id=booking.id,
            old_value=old_status,
            new_value=BookingStatus.CANCELLED
        )

        return updated_booking

    async def approve_booking(self, booking_id: int, approver: User, note: str = None) -> Booking:
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลการจอง")
        
        if booking.status != BookingStatus.PENDING:
            raise HTTPException(status_code=400, detail="สามารถอนุมัติได้เฉพาะการจองที่รอการอนุมัติเท่านั้น")

        # 1. Update Booking Status
        booking.status = BookingStatus.CONFIRMED
        
        # 2. Create Approval Record (Separate Table per SSOT)
        approval = BookingApproval(
            booking_id=booking.id,
            approver_id=approver.id,
            action="approved",
            reason=note
        )
        self.db.add(approval)
        
        updated_booking = await self.booking_repo.update(booking)

        # Audit Log
        await self.audit_service.log_action(
            user_id=approver.id,
            action="booking.approve",
            resource_type="booking",
            resource_id=booking.id,
            old_value="pending",
            new_value="confirmed"
        )

        await event_manager.emit("booking.approved", booking=updated_booking)
        return updated_booking

    async def reject_booking(self, booking_id: int, approver: User, note: str) -> Booking:
        if not note:
            raise HTTPException(status_code=400, detail="กรุณาระบุเหตุผลในการปฏิเสธ")

        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลการจอง")
        
        if booking.status != BookingStatus.PENDING:
            raise HTTPException(status_code=400, detail="สามารถปฏิเสธได้เฉพาะการจองที่รอการอนุมัติเท่านั้น")

        booking.status = BookingStatus.REJECTED
        
        # Create Approval Record
        approval = BookingApproval(
            booking_id=booking.id,
            approver_id=approver.id,
            action="rejected",
            reason=note
        )
        self.db.add(approval)
        
        updated_booking = await self.booking_repo.update(booking)

        # Audit Log
        await self.audit_service.log_action(
            user_id=approver.id,
            action="booking.reject",
            resource_type="booking",
            resource_id=booking.id,
            old_value="pending",
            new_value="rejected"
        )

        await event_manager.emit("booking.rejected", booking=updated_booking, note=note)
        return updated_booking

    async def get_booking_detail(self, booking_id: int, user: User) -> Booking:
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลการจอง")
        
        # Check permission (Admin or owner)
        if user.role != "admin" and booking.user_id != user.id:
            raise HTTPException(status_code=403, detail="คุณไม่มีสิทธิ์เข้าถึงข้อมูลการจองนี้")
            
        return booking

    async def update_booking(self, booking_id: int, user: User, data: BookingUpdate) -> Booking:
        booking = await self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลการจอง")
        
        # Permission: Owner or Admin
        if user.role != "admin" and booking.user_id != user.id:
            raise HTTPException(status_code=403, detail="คุณไม่มีสิทธิ์แก้ไขการจองนี้")
        
        # Check if booking is in editable state
        if booking.status in [BookingStatus.CANCELLED, BookingStatus.REJECTED]:
            raise HTTPException(status_code=400, detail=f"ไม่สามารถแก้ไขการจองที่มีสถานะ {booking.status} ได้")

        # Prepare Audit
        old_values = {}
        for field in ["title", "description", "start_time", "end_time", "attendee_count"]:
            old_values[field] = str(getattr(booking, field))

        # Update fields
        has_time_change = False
        if data.start_time is not None or data.end_time is not None:
            new_start = data.start_time or booking.start_time
            new_end = data.end_time or booking.end_time
            
            if new_start >= new_end:
                raise HTTPException(status_code=400, detail="เวลาสิ้นสุดต้องมากกว่าเวลาเริ่มต้น")
            
            # Conflict check
            enable_conflict_check = await self.config_service.get_value("ENABLE_CONFLICT_CHECK", True)
            if enable_conflict_check:
                conflicts = await self.booking_repo.find_conflicts(booking.room_id, new_start, new_end, exclude_id=booking_id)
                if conflicts:
                    raise HTTPException(status_code=409, detail="ช่วงเวลาดังกล่าวถูกจองไปแล้ว กรุณาเลือกช่วงเวลาอื่น")
            
            booking.start_time = new_start
            booking.end_time = new_end
            has_time_change = True

        if data.title is not None:
            booking.title = data.title
        if data.description is not None:
            booking.description = data.description
        if data.attendee_count is not None:
            booking.attendee_count = data.attendee_count

        # SSOT: If a confirmed booking is edited by a non-admin, reset to PENDING
        old_status = booking.status
        if user.role != "admin" and booking.status == BookingStatus.CONFIRMED:
            booking.status = BookingStatus.PENDING

        updated_booking = await self.booking_repo.update(booking)

        # Audit Log
        await self.audit_service.log_action(
            user_id=user.id,
            action="booking.update",
            resource_type="booking",
            resource_id=booking.id,
            old_value=json.dumps(old_values),
            new_value=json.dumps({
                "title": booking.title,
                "start_time": str(booking.start_time),
                "end_time": str(booking.end_time),
                "status": booking.status
            })
        )

        return updated_booking

    async def duplicate_booking(self, booking_id: int, user: User) -> Booking:
        # This is a helper to get data for duplication, 
        # but usually we can just use create_booking from frontend.
        # However, let's provide a server-side duplication if needed.
        original = await self.booking_repo.get_by_id(booking_id)
        if not original:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลการจองต้นฉบับ")
        
        # Return a new booking object (not saved yet) or just the data
        # For simplicity, we'll let the frontend handle the "Duplicate" by 
        # fetching the detail and sending it to the create endpoint.
        return original

    async def reschedule_booking(self, booking_id: int, user: User, start_time: datetime, end_time: datetime) -> Booking:
        # Wrap the new update_booking for backward compatibility
        return await self.update_booking(booking_id, user, BookingUpdate(start_time=start_time, end_time=end_time))

    async def cleanup_expired_bookings(self, minutes: int = 30):
        # ... existing logic ...
        return 0
