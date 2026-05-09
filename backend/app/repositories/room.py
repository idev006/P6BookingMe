from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.room import Room, RoomEquipment, RoomImage, RoomStatus

class RoomRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, room: Room) -> Room:
        self.session.add(room)
        await self.session.commit()
        await self.session.refresh(room)
        return room

    async def get_by_id(self, room_id: int) -> Room | None:
        query = select(Room).where(Room.id == room_id).options(
            selectinload(Room.equipment),
            selectinload(Room.images)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_name_and_building(self, name: str, building: str | None) -> Room | None:
        query = select(Room).where(Room.name == name, Room.building == building)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        status: RoomStatus | None = None,
        search: str | None = None,
        min_capacity: int | None = None
    ) -> list[Room]:
        query = select(Room).options(
            selectinload(Room.equipment),
            selectinload(Room.images)
        )
        
        if status:
            query = query.where(Room.status == status)
        if min_capacity:
            query = query.where(Room.capacity >= min_capacity)
        if search:
            search_filter = or_(
                Room.name.ilike(f"%{search}%"),
                Room.location.ilike(f"%{search}%"),
                Room.building.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(
        self, 
        status: RoomStatus | None = None,
        search: str | None = None,
        min_capacity: int | None = None
    ) -> int:
        query = select(func.count()).select_from(Room)
        if status:
            query = query.where(Room.status == status)
        if min_capacity:
            query = query.where(Room.capacity >= min_capacity)
        if search:
            search_filter = or_(
                Room.name.ilike(f"%{search}%"),
                Room.location.ilike(f"%{search}%"),
                Room.building.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def update(self, room: Room) -> Room:
        await self.session.commit()
        await self.session.refresh(room)
        return room

    async def delete_equipment_by_room(self, room_id: int):
        from sqlalchemy import delete
        query = delete(RoomEquipment).where(RoomEquipment.room_id == room_id)
        await self.session.execute(query)
        await self.session.commit()

    async def add_image(self, image: RoomImage) -> RoomImage:
        self.session.add(image)
        await self.session.commit()
        await self.session.refresh(image)
        return image

    async def get_image(self, image_id: int) -> RoomImage | None:
        query = select(RoomImage).where(RoomImage.id == image_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_image(self, image: RoomImage):
        await self.session.delete(image)
        await self.session.commit()

    async def unset_primary_images(self, room_id: int):
        from sqlalchemy import update
        query = update(RoomImage).where(RoomImage.room_id == room_id).values(is_primary=False)
        await self.session.execute(query)
        await self.session.commit()

    async def delete(self, room: Room):
        await self.session.delete(room)
        await self.session.commit()
