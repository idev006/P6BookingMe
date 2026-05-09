from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum
from datetime import datetime

class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    MAINTENANCE = "maintenance"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    attendee_count = Column(Integer, nullable=False, default=0)
    
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    cancel_reason = Column(Text, nullable=True)
    cancelled_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # ── Snapshot ── (Frozen data at the time of booking)
    snap_room_name = Column(String(255), nullable=False)
    snap_room_capacity = Column(Integer, nullable=False)
    snap_room_location = Column(String(255), nullable=False)
    snap_user_name = Column(String(255), nullable=False)
    snap_user_department = Column(String(255), nullable=False)
    snap_user_email = Column(String(255), nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="bookings", foreign_keys=[user_id])
    room = relationship("Room", back_populates="bookings")
    canceller = relationship("User", foreign_keys=[cancelled_by])
    approval = relationship("BookingApproval", back_populates="booking", uselist=False, cascade="all, delete-orphan")

class BookingApproval(Base):
    __tablename__ = "booking_approvals"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), unique=True, nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    action = Column(String(20), nullable=False) # 'approved', 'rejected'
    reason = Column(Text, nullable=True)
    actioned_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    booking = relationship("Booking", back_populates="approval")
    approver = relationship("User")
