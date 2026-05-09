from fastapi import HTTPException, UploadFile
from app.models.audit_log import AuditLog
from app.schemas.room import RoomCreate, RoomUpdate
from app.models.room import Room, RoomEquipment, RoomImage, RoomStatus
from app.repositories.room import RoomRepository
from app.repositories.audit_log import AuditLogRepository
from app.utils.file_upload import save_upload_file, delete_physical_file

# In-memory Cache for Room List (Sprint 5.3 Performance)
_ROOM_LIST_CACHE = None

class RoomService:
    def __init__(self, room_repo: RoomRepository, audit_repo: AuditLogRepository):
        self.room_repo = room_repo
        self.audit_repo = audit_repo

    def _invalidate_cache(self):
        global _ROOM_LIST_CACHE
        _ROOM_LIST_CACHE = None

    async def create_room(self, data: RoomCreate, admin_id: int, ip_address: str | None = None) -> Room:
        # Check uniqueness: name + building
        existing = await self.room_repo.get_by_name_and_building(data.name, data.building)
        if existing:
            raise HTTPException(status_code=400, detail=f"ห้องชื่อ '{data.name}' มีอยู่แล้วในอาคาร '{data.building or 'Default'}'")

        room = Room(
            name=data.name,
            capacity=data.capacity,
            location=data.location,
            building=data.building,
            floor=data.floor,
            description=data.description
        )
        
        # Add equipment
        if data.equipment:
            room.equipment = [RoomEquipment(name=name) for name in data.equipment]
            
        new_room = await self.room_repo.create(room)
        self._invalidate_cache()
        
        # Audit Log
        await self.audit_repo.create(AuditLog(
            user_id=admin_id,
            action="room.create",
            entity_type="room",
            entity_id=new_room.id,
            new_value=data.model_dump(),
            ip_address=ip_address
        ))
        
        return new_room

    async def get_rooms(self, **kwargs):
        global _ROOM_LIST_CACHE
        
        # Simple Cache Logic: Only cache full active room list (most common)
        is_default_query = not kwargs.get("search") and kwargs.get("status") == RoomStatus.ACTIVE
        
        if is_default_query and _ROOM_LIST_CACHE is not None:
            return _ROOM_LIST_CACHE
            
        rooms = await self.room_repo.get_multi(**kwargs)
        total = await self.room_repo.count(
            status=kwargs.get("status"),
            search=kwargs.get("search"),
            min_capacity=kwargs.get("min_capacity")
        )
        
        result = (rooms, total)
        
        if is_default_query:
            _ROOM_LIST_CACHE = result
            
        return result

    async def get_room(self, room_id: int) -> Room:
        room = await self.room_repo.get_by_id(room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        return room

    async def update_room(self, room_id: int, data: RoomUpdate, admin_id: int, ip_address: str | None = None) -> Room:
        room = await self.get_room(room_id)
        
        old_value = {
            "name": room.name,
            "capacity": room.capacity,
            "status": room.status
        }
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Check uniqueness if name or building is changing
        new_name = update_data.get("name", room.name)
        new_building = update_data.get("building", room.building)
        if new_name != room.name or new_building != room.building:
            existing = await self.room_repo.get_by_name_and_building(new_name, new_building)
            if existing and existing.id != room_id:
                raise HTTPException(status_code=400, detail=f"ห้องชื่อ '{new_name}' มีอยู่แล้วในอาคาร '{new_building or 'Default'}'")

        for field, value in update_data.items():
            setattr(room, field, value)
            
        updated_room = await self.room_repo.update(room)
        self._invalidate_cache()
        
        # Audit Log
        await self.audit_repo.create(AuditLog(
            user_id=admin_id,
            action="room.update",
            entity_type="room",
            entity_id=room_id,
            old_value=old_value,
            new_value=update_data,
            ip_address=ip_address
        ))
        
        return updated_room

    async def deactivate_room(self, room_id: int, admin_id: int, ip_address: str | None = None) -> Room:
        return await self.update_room(
            room_id, 
            RoomUpdate(status=RoomStatus.INACTIVE), 
            admin_id, 
            ip_address
        )

    async def activate_room(self, room_id: int, admin_id: int, ip_address: str | None = None) -> Room:
        return await self.update_room(
            room_id, 
            RoomUpdate(status=RoomStatus.ACTIVE), 
            admin_id, 
            ip_address
        )

    async def add_room_image(self, room_id: int, file: UploadFile, admin_id: int, ip_address: str | None = None) -> RoomImage:
        room = await self.get_room(room_id)
        
        # Save file
        relative_path = await save_upload_file(file, f"rooms/{room_id}")
        
        # If first image, make it primary
        is_primary = len(room.images) == 0
        
        image = RoomImage(
            room_id=room_id,
            image_path=relative_path,
            is_primary=is_primary
        )
        
        new_image = await self.room_repo.add_image(image)
        
        # Audit
        await self.audit_repo.create(AuditLog(
            user_id=admin_id,
            action="room.image_upload",
            entity_type="room",
            entity_id=room_id,
            new_value={"image_id": new_image.id, "path": relative_path},
            ip_address=ip_address
        ))
        
        return new_image

    async def delete_room_image(self, room_id: int, image_id: int, admin_id: int, ip_address: str | None = None):
        image = await self.room_repo.get_image(image_id)
        if not image or image.room_id != room_id:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Delete from disk
        delete_physical_file(image.image_path)
        
        # Delete from DB
        await self.room_repo.delete_image(image)
        
        # Audit
        await self.audit_repo.create(AuditLog(
            user_id=admin_id,
            action="room.image_delete",
            entity_type="room",
            entity_id=room_id,
            old_value={"image_id": image_id, "path": image.image_path},
            ip_address=ip_address
        ))

    async def set_primary_image(self, room_id: int, image_id: int, admin_id: int, ip_address: str | None = None):
        image = await self.room_repo.get_image(image_id)
        if not image or image.room_id != room_id:
            raise HTTPException(status_code=404, detail="Image not found")
        
        # Unset all other primary images
        await self.room_repo.unset_primary_images(room_id)
        
        # Set this one as primary
        image.is_primary = True
        await self.room_repo.update(image) # This works because update commits session
        
        # Audit
        await self.audit_repo.create(AuditLog(
            user_id=admin_id,
            action="room.image_set_primary",
            entity_type="room",
            entity_id=room_id,
            new_value={"image_id": image_id},
            ip_address=ip_address
        ))

    async def delete_room(self, room_id: int, admin_id: int, ip_address: str | None = None):
        room = await self.get_room(room_id)
        
        # 0. Check for existing bookings (Technical Excellence)
        # In a real scenario, we check if there are any CONFIRMED or PENDING bookings
        from sqlalchemy import select, func
        from app.models.booking import Booking, BookingStatus
        
        # We need a db session to run this check, since room_repo has it
        stmt = select(func.count()).select_from(Booking).where(
            Booking.room_id == room_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        )
        result = await self.room_repo.session.execute(stmt)
        count = result.scalar()
        
        if count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"ไม่สามารถลบห้องได้ เนื่องจากมีการจองที่ค้างอยู่ {count} รายการ"
            )

        # 1. Physical Cleanup
        for image in room.images:
            try:
                delete_physical_file(image.image_path)
            except Exception as e:
                import logging
                logging.error(f"Failed to delete physical file {image.image_path}: {e}")
        
        # 2. Delete from DB
        await self.room_repo.delete(room)
        self._invalidate_cache()
        
        # 3. Audit
        await self.audit_repo.create(AuditLog(
            user_id=admin_id,
            action="room.delete",
            entity_type="room",
            entity_id=room_id,
            old_value={"name": room.name, "image_count": len(room.images)},
            ip_address=ip_address
        ))
