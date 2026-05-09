from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.schemas.system_config import ConfigResponse, ConfigUpdate
from app.services.config_service import ConfigService
from app.services.audit import AuditService
from app.schemas.common import StandardResponse
from typing import List
import json

router = APIRouter()

@router.get("/", response_model=StandardResponse)
async def list_configs(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = ConfigService(db)
    configs = await service.list_all_configs()
    return StandardResponse(
        data=[ConfigResponse.model_validate(c) for c in configs]
    )

@router.patch("/{key}", response_model=StandardResponse)
async def update_config(
    key: str,
    body: ConfigUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    service = ConfigService(db)
    audit_service = AuditService(db)
    
    # 1. Get old value for audit
    config = await service.repo.get_by_key(key)
    if not config:
        raise HTTPException(status_code=404, detail="Config key not found")
    
    old_value = config.value
    
    # 2. Update
    updated = await service.set_value(key, body.value, current_user.id)
    
    # 3. Audit Log
    await audit_service.log_action(
        user_id=current_user.id,
        action="config.update",
        resource_type="system_config",
        resource_id=updated.id,
        old_value=str(old_value),
        new_value=str(body.value)
    )
    
    return StandardResponse(
        data=ConfigResponse.model_validate(updated),
        message=f"อัปเดตการตั้งค่า {key} เรียบร้อยแล้ว"
    )
