from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.notification import NotificationType

class NotificationResponse(BaseModel):
    id: int
    type: NotificationType
    message: str
    booking_id: int | None
    is_read: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
