from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.notification import NotificationService
from app.schemas.notification import NotificationResponse
from app.schemas.common import StandardResponse
from typing import List

router = APIRouter()

@router.get("", response_model=StandardResponse)
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 10
):
    service = NotificationService(db)
    notifications = await service.get_my_notifications(current_user.id, limit)
    return StandardResponse(data=[NotificationResponse.model_validate(n) for n in notifications])

@router.post("/read-all", response_model=StandardResponse)
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    await service.mark_all_as_read(current_user.id)
    return StandardResponse(message="ทำเครื่องหมายว่าอ่านแล้วทั้งหมดเรียบร้อยแล้ว")
