from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.models.booking import BookingStatus

class BookingBase(BaseModel):
    room_id: int
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    attendee_count: int = Field(..., ge=1)

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attendee_count: Optional[int] = Field(None, ge=1)
    status: Optional[BookingStatus] = None

class BookingResponse(BookingBase):
    id: int
    user_id: int
    status: BookingStatus
    attendee_count: int
    
    # Snapshots
    snap_room_name: Optional[str] = None
    snap_room_location: Optional[str] = None
    snap_room_capacity: Optional[int] = None
    snap_user_name: Optional[str] = None
    snap_user_email: Optional[str] = None
    snap_user_department: Optional[str] = None
    
    room_snapshot: Optional[dict] = None
    approval_note: Optional[str] = None
    approved_by: Optional[int] = None
    approved_by_name: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class BookingReschedule(BaseModel):
    start_time: datetime
    end_time: datetime

class BookingListResponse(BaseModel):
    total: int
    data: List[BookingResponse]
