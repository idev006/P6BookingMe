from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import require_admin
from app.models.user import User
from app.services.audit import AuditService
from app.schemas.common import StandardResponse

router = APIRouter()

@router.get("", response_model=StandardResponse)
async def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = Query(None),
    resource_type: str | None = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select, func, or_
    from sqlalchemy.orm import selectinload
    from app.models.audit_log import AuditLog
    
    stmt = select(AuditLog).options(selectinload(AuditLog.user))
    count_stmt = select(func.count()).select_from(AuditLog)
    
    # Filtering
    if resource_type and resource_type != 'all':
        stmt = stmt.where(AuditLog.entity_type == resource_type)
        count_stmt = count_stmt.where(AuditLog.entity_type == resource_type)
        
    if search:
        q = f"%{search}%"
        # Since user is a relation, we might need a join if we want to search by user name
        from app.models.user import User as UserModel
        stmt = stmt.join(AuditLog.user, isouter=True)
        count_stmt = count_stmt.join(AuditLog.user, isouter=True)
        
        search_filter = or_(
            AuditLog.action.ilike(q),
            AuditLog.entity_type.ilike(q),
            UserModel.full_name.ilike(q)
        )
        stmt = stmt.where(search_filter)
        count_stmt = count_stmt.where(search_filter)
        
    total = await db.scalar(count_stmt)
    
    stmt = stmt.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    return StandardResponse(
        data={
            "data": [{
                "id": log.id,
                "user_id": log.user_id,
                "user_name": log.user.full_name if log.user else "System",
                "action": log.action,
                "resource_type": log.entity_type,
                "resource_id": log.entity_id,
                "old_value": log.old_value,
                "new_value": log.new_value,
                "ip_address": log.ip_address,
                "created_at": log.created_at
            } for log in logs],
            "total": total
        }
    )
