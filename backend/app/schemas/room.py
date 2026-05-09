from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.room import RoomStatus

class RoomEquipmentBase(BaseModel):
    name: str

class RoomEquipmentCreate(RoomEquipmentBase):
    pass

class RoomEquipmentResponse(RoomEquipmentBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class RoomImageResponse(BaseModel):
    id: int
    image_path: str
    is_primary: bool
    model_config = ConfigDict(from_attributes=True)

class RoomBase(BaseModel):
    name: str = Field(..., max_length=255)
    capacity: int = Field(..., gt=0)
    location: str = Field(..., max_length=255)
    building: str | None = Field(None, max_length=100)
    floor: str | None = Field(None, max_length=20)
    description: str | None = None

class RoomCreate(RoomBase):
    equipment: list[str] = [] # List of equipment names

class RoomUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    capacity: int | None = Field(None, gt=0)
    location: str | None = Field(None, max_length=255)
    building: str | None = Field(None, max_length=100)
    floor: str | None = Field(None, max_length=20)
    description: str | None = None
    status: RoomStatus | None = None

class RoomResponse(RoomBase):
    id: int
    status: RoomStatus
    created_at: datetime
    updated_at: datetime
    equipment: list[RoomEquipmentResponse] = []
    images: list[RoomImageResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
