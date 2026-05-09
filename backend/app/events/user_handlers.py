from app.services.event_manager import event_manager
from app.services.notification import NotificationService, NotificationType
from app.core.database import AsyncSessionLocal
from app.core.context import get_request_id
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

async def handle_user_approved(user: User):
    req_id = get_request_id()
    try:
        async with AsyncSessionLocal() as db:
            notification_service = NotificationService(db)
            await notification_service.create_notification(
                user_id=user.id,
                type=NotificationType.SYSTEM,
                message="ยินดีต้อนรับ! บัญชีของคุณได้รับการอนุมัติแล้ว คุณสามารถเริ่มจองห้องประชุมได้ทันที"
            )
            logger.info(f"[{req_id}] Welcome notification created for user {user.id}")
    except Exception as e:
        logger.error(f"[{req_id}] Failed to create welcome notification for user {user.id}: {e}")

def register_user_handlers():
    event_manager.subscribe("user.approved", handle_user_approved)
