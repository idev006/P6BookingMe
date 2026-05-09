from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import require_admin
from app.models.user import User, UserStatus
from app.schemas.user import UserResponse
from app.schemas.common import StandardResponse
from app.services.audit import AuditService
from app.services.event_manager import event_manager
from sqlalchemy import select, func
import json

router = APIRouter()

@router.get("/", response_model=StandardResponse)
async def list_users(
    status: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import or_
    stmt = select(User)
    count_stmt = select(func.count()).select_from(User)
    
    # Filtering
    if status and status != 'all':
        stmt = stmt.where(User.status == status)
        count_stmt = count_stmt.where(User.status == status)
    if role and role != 'all':
        stmt = stmt.where(User.role == role)
        count_stmt = count_stmt.where(User.role == role)
    
    if search:
        q = f"%{search}%"
        search_filter = or_(
            User.full_name.ilike(q),
            User.email.ilike(q),
            User.employee_code.ilike(q)
        )
        stmt = stmt.where(search_filter)
        count_stmt = count_stmt.where(search_filter)
        
    total = await db.scalar(count_stmt)
    
    stmt = stmt.order_by(User.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    return StandardResponse(data={
        "data": [UserResponse.model_validate(u) for u in users],
        "total": total
    })

@router.post("/{user_id}/approve/", response_model=StandardResponse)
async def approve_member(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.status != UserStatus.PENDING:
        raise HTTPException(status_code=400, detail="User is not in pending status")
    
    user.status = UserStatus.ACTIVE
    db.add(user)
    await db.commit()
    
    # Trigger Event
    await event_manager.emit("user.approved", user)
    
    # Audit Log
    audit = AuditService(db)
    await audit.log_action(
        user_id=current_user.id,
        action="user.approve",
        resource_type="user",
        resource_id=user_id,
        new_value="active"
    )
    
    return StandardResponse(message="อนุมัติสมาชิกเรียบร้อยแล้ว")

@router.post("/{user_id}/reject/", response_model=StandardResponse)
async def reject_member(
    user_id: int,
    reason: str = Body(..., embed=True),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.status != UserStatus.PENDING:
        raise HTTPException(status_code=400, detail="User is not in pending status")
    
    user.status = UserStatus.REJECTED
    db.add(user)
    await db.commit()
    
    # Audit Log
    audit = AuditService(db)
    await audit.log_action(
        user_id=current_user.id,
        action="user.reject",
        resource_type="user",
        resource_id=user_id,
        new_value="rejected",
        reason=reason
    )
    
    return StandardResponse(message=f"ปฏิเสธการสมัครสมาชิกเรียบร้อยแล้ว (เหตุผล: {reason})")

@router.post("/{user_id}/role/", response_model=StandardResponse)
async def update_user_role(
    user_id: int,
    role: str = Body(..., embed=True),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_role = user.role
    user.role = role
    db.add(user)
    await db.commit()
    
    # Audit Log
    audit = AuditService(db)
    await audit.log_action(
        user_id=current_user.id,
        action="user.update_role",
        resource_type="user",
        resource_id=user_id,
        old_value=old_role,
        new_value=role
    )
    
    return StandardResponse(message=f"อัปเดตสิทธิ์เป็น {role} เรียบร้อยแล้ว")

@router.post("/{user_id}/status/", response_model=StandardResponse)
async def update_user_status(
    user_id: int,
    status: str = Body(..., embed=True),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_status = user.status
    user.status = status
    db.add(user)
    await db.commit()
    
    # Audit Log
    audit = AuditService(db)
    await audit.log_action(
        user_id=current_user.id,
        action="user.update_status",
        resource_type="user",
        resource_id=user_id,
        old_value=old_status,
        new_value=status
    )
    
    return StandardResponse(message=f"อัปเดตสถานะเป็น {status} เรียบร้อยแล้ว")

@router.post("/{user_id}/anonymize/", response_model=StandardResponse)
async def anonymize_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    import uuid
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.role == "admin" and user.id == current_user.id:
        raise HTTPException(status_code=400, detail="ไม่สามารถลบข้อมูลของตนเองได้")
        
    # PDPA Anonymization logic
    old_data = {
        "full_name": user.full_name,
        "email": user.email,
        "employee_code": user.employee_code,
        "department": user.department,
        "phone": user.phone,
        "status": user.status
    }
    
    random_uuid = str(uuid.uuid4())
    user.full_name = "Anonymous User"
    user.email = f"deleted_{random_uuid}@anonymized.local"
    user.employee_code = f"DEL_{random_uuid[:8]}"
    user.department = "Deleted"
    user.phone = None
    user.status = UserStatus.DELETED
    
    # If the user model dynamically supports avatar_path from users.py
    if hasattr(user, 'avatar_path'):
        user.avatar_path = None
        
    db.add(user)
    await db.commit()
    
    # Audit Log
    audit = AuditService(db)
    await audit.log_action(
        user_id=current_user.id,
        action="user.anonymize",
        resource_type="user",
        resource_id=user_id,
        old_value=json.dumps(old_data),
        new_value="anonymized"
    )
    
    return StandardResponse(message="ดำเนินการลบข้อมูลตาม PDPA เรียบร้อยแล้ว")
