from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from app.repositories.audit_log import AuditLogRepository
import json

class AuditService:
    def __init__(self, db: AsyncSession):
        self.repo = AuditLogRepository(db)

    async def log_action(
        self, 
        user_id: int, 
        action: str, 
        resource_type: str, 
        resource_id: int | None = None, 
        old_value: any = None, 
        new_value: any = None, 
        ip_address: str | None = None
    ):
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=resource_type,
            entity_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address
        )
        await self.repo.create(log)
