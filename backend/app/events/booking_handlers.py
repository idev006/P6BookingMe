from app.services.event_manager import event_manager
from app.services.notification import NotificationService, NotificationType
from app.core.database import AsyncSessionLocal
from app.core.context import get_request_id
from app.models.booking import Booking
import logging

logger = logging.getLogger(__name__)

async def handle_booking_approved(booking: Booking):
    req_id = get_request_id()
    try:
        async with AsyncSessionLocal() as db:
            notification_service = NotificationService(db)
            await notification_service.create_notification(
                user_id=booking.user_id,
                type=NotificationType.BOOKING_CONFIRMED,
                message=f"การจองห้อง {booking.snap_room_name} ในวันที่ {booking.start_time.strftime('%d/%m/%Y')} ได้รับการอนุมัติแล้ว",
                booking_id=booking.id
            )
            logger.info(f"[{req_id}] Notification created for approved booking {booking.id}")
    except Exception as e:
        logger.error(f"[{req_id}] Failed to create approval notification for booking {booking.id}: {e}")

async def handle_booking_rejected(booking: Booking, note: str):
    req_id = get_request_id()
    try:
        async with AsyncSessionLocal() as db:
            notification_service = NotificationService(db)
            await notification_service.create_notification(
                user_id=booking.user_id,
                type=NotificationType.BOOKING_REJECTED,
                message=f"การจองห้อง {booking.snap_room_name} ถูกปฏิเสธเนื่องจาก: {note}",
                booking_id=booking.id
            )
            logger.info(f"[{req_id}] Notification created for rejected booking {booking.id}")
    except Exception as e:
        logger.error(f"[{req_id}] Failed to create rejection notification for booking {booking.id}: {e}")

def register_booking_handlers():
    event_manager.subscribe("booking.approved", handle_booking_approved)
    event_manager.subscribe("booking.rejected", handle_booking_rejected)
