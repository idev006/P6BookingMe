from fastapi import APIRouter, Depends, Query, Request, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.room import RoomRepository
from app.repositories.audit_log import AuditLogRepository
from app.services.room import RoomService
from app.schemas.room import RoomResponse, RoomCreate, RoomUpdate, RoomImageResponse
from app.schemas.common import StandardResponse
from app.models.room import RoomStatus
from app.api.deps import get_current_user, require_admin
from app.models.user import User, UserRole

router = APIRouter()

def get_room_service(db: AsyncSession = Depends(get_db)) -> RoomService:
    room_repo = RoomRepository(db)
    audit_repo = AuditLogRepository(db)
    return RoomService(room_repo, audit_repo)

# --- PUBLIC / MEMBER Endpoints ---

@router.get("/", response_model=StandardResponse)
async def get_rooms(
    skip: int = 0,
    limit: int = 20,
    search: str | None = None,
    min_capacity: int | None = None,
    status: str | None = Query(None, description="active, inactive, or all (Admin only)"),
    current_user: User = Depends(get_current_user),
    service: RoomService = Depends(get_room_service)
):
    # Default for members: only ACTIVE
    status_filter = RoomStatus.ACTIVE
    
    # If admin, allow filtering by status or 'all'
    if current_user.role == UserRole.ADMIN:
        if status == "all":
            status_filter = None
        elif status == "inactive":
            status_filter = RoomStatus.INACTIVE
        elif status == "active":
            status_filter = RoomStatus.ACTIVE

    rooms, total = await service.get_rooms(
        skip=skip, 
        limit=limit, 
        status=status_filter, 
        search=search, 
        min_capacity=min_capacity
    )
    return StandardResponse(data={
        "data": [RoomResponse.model_validate(r).model_dump(mode='json') for r in rooms],
        "total": total
    })

@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    service: RoomService = Depends(get_room_service)
):
    return await service.get_room(room_id)

# --- ADMIN Endpoints ---

@router.post("/", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    request: Request,
    data: RoomCreate,
    current_admin: User = Depends(require_admin),
    service: RoomService = Depends(get_room_service)
):
    return await service.create_room(data, current_admin.id, ip_address=request.client.host)

@router.patch("/{room_id}", response_model=RoomResponse)
async def update_room(
    request: Request,
    room_id: int,
    data: RoomUpdate,
    current_admin: User = Depends(require_admin),
    service: RoomService = Depends(get_room_service)
):
    return await service.update_room(room_id, data, current_admin.id, ip_address=request.client.host)

@router.post("/{room_id}/deactivate/", response_model=RoomResponse)
async def deactivate_room(
    request: Request,
    room_id: int,
    current_admin: User = Depends(require_admin),
    service: RoomService = Depends(get_room_service)
):
    return await service.deactivate_room(room_id, current_admin.id, ip_address=request.client.host)

@router.post("/{room_id}/activate/", response_model=RoomResponse)
async def activate_room(
    request: Request,
    room_id: int,
    current_admin: User = Depends(require_admin),
    service: RoomService = Depends(get_room_service)
):
    return await service.activate_room(room_id, current_admin.id, ip_address=request.client.host)

# --- IMAGE Management ---

@router.post("/{room_id}/images/", response_model=RoomImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_room_image(
    request: Request,
    room_id: int,
    file: UploadFile = File(...),
    current_admin: User = Depends(require_admin),
    service: RoomService = Depends(get_room_service)
):
    return await service.add_room_image(room_id, file, current_admin.id, ip_address=request.client.host)

@router.delete("/{room_id}/images/{image_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room_image(
    request: Request,
    room_id: int,
    image_id: int,
    current_admin: User = Depends(require_admin),
    service: RoomService = Depends(get_room_service)
):
    await service.delete_room_image(room_id, image_id, current_admin.id, ip_address=request.client.host)
    return None

@router.post("/{room_id}/images/{image_id}/set-primary/", response_model=dict)
async def set_primary_image(
    request: Request,
    room_id: int,
    image_id: int,
    current_admin: User = Depends(require_admin),
    service: RoomService = Depends(get_room_service)
):
    await service.set_primary_image(room_id, image_id, current_admin.id, ip_address=request.client.host)
    return {"message": "ตั้งค่ารูปหลักเรียบร้อยแล้ว"}
