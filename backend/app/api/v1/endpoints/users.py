from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.audit import AuditService
from app.schemas.common import StandardResponse
from app.core.config import settings
import os
import uuid
import json

router = APIRouter()

@router.get("/me/", response_model=StandardResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return StandardResponse(data=current_user)

@router.patch("/me/", response_model=StandardResponse)
async def update_profile(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    audit_service = AuditService(db)
    
    # Audit Log - Old values
    old_data = {
        "full_name": current_user.full_name,
        "phone": current_user.phone
    }
    
    # Update fields (Strictly allow only certain fields)
    if body.full_name is not None:
        current_user.full_name = body.full_name
    if body.phone is not None:
        current_user.phone = body.phone
        
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    # Audit Log
    await audit_service.log_action(
        user_id=current_user.id,
        action="user.update_profile",
        resource_type="user",
        resource_id=current_user.id,
        old_value=json.dumps(old_data),
        new_value=json.dumps(body.model_dump(exclude_unset=True))
    )
    
    return StandardResponse(data=current_user, message="อัปเดตข้อมูลส่วนตัวเรียบร้อยแล้ว")

@router.post("/me/avatar/", response_model=StandardResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Ensure directory exists
    avatar_dir = os.path.join(settings.UPLOADS_DIR, "avatars")
    os.makedirs(avatar_dir, exist_ok=True)
    
    # Generate filename
    ext = os.path.splitext(file.filename)[1]
    filename = f"{current_user.id}_{uuid.uuid4().hex}{ext}"
    file_path = os.path.join("avatars", filename)
    full_path = os.path.join(settings.UPLOADS_DIR, file_path)
    
    # Save file
    with open(full_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    # Update user record
    current_user.avatar_path = file_path
    db.add(current_user)
    await db.commit()
    
    return StandardResponse(data={"avatar_path": file_path}, message="อัปโหลดรูปโปรไฟล์เรียบร้อยแล้ว")
