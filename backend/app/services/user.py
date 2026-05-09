from fastapi import HTTPException, status
from app.models.user import User, UserStatus, UserRole
from app.repositories.user import UserRepository
from app.repositories.audit_log import AuditLogRepository
from app.models.audit_log import AuditLog
from app.services.notification import NotificationService
from app.models.notification import NotificationType

class UserService:
    def __init__(self, user_repo: UserRepository, audit_repo: AuditLogRepository, notification_service: NotificationService):
        self.user_repo = user_repo
        self.audit_repo = audit_repo
        self.notification_service = notification_service

    async def get_users(
        self, 
        skip: int = 0, 
        limit: int = 20, 
        status: str | None = None, 
        role: str | None = None, 
        search: str | None = None
    ) -> tuple[list[User], int]:
        users = await self.user_repo.get_multi(
            skip=skip, limit=limit, status=status, role=role, search=search
        )
        total = await self.user_repo.count(status=status, role=role, search=search)
        return users, total

    async def approve_user(self, user_id: int, admin_id: int, ip_address: str | None = None) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.status == UserStatus.ACTIVE:
            return user
            
        old_status = user.status
        user.status = UserStatus.ACTIVE
        updated_user = await self.user_repo.update(user)
        
        await self.audit_repo.create(AuditLog(
            user_id=admin_id,
            action="user.approve",
            entity_type="user",
            entity_id=user_id,
            old_value={"status": old_status},
            new_value={"status": UserStatus.ACTIVE},
            ip_address=ip_address
        ))

        # ส่ง Notification แจ้งผู้ใช้
        await self.notification_service.notify_user(
            user_id=user_id,
            type=NotificationType.USER_APPROVED,
            message="บัญชีของคุณได้รับการอนุมัติแล้ว คุณสามารถเริ่มต้นจองห้องประชุมได้ทันที"
        )

        return updated_user

    async def reject_user(self, user_id: int, admin_id: int, reason: str, ip_address: str | None = None) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        old_status = user.status
        user.status = UserStatus.REJECTED
        updated_user = await self.user_repo.update(user)
        
        await self.audit_repo.create(AuditLog(
            user_id=admin_id,
            action="user.reject",
            entity_type="user",
            entity_id=user_id,
            old_value={"status": old_status},
            new_value={"status": UserStatus.REJECTED, "reason": reason},
            ip_address=ip_address
        ))

        # ส่ง Notification แจ้งผู้ใช้
        await self.notification_service.notify_user(
            user_id=user_id,
            type=NotificationType.USER_REJECTED,
            message=f"บัญชีของคุณไม่ผ่านการอนุมัติ เนื่องจาก: {reason}"
        )

        return updated_user

    async def suspend_user(self, user_id: int, admin_id: int, reason: str, ip_address: str | None = None) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        old_status = user.status
        user.status = UserStatus.SUSPENDED
        updated_user = await self.user_repo.update(user)
        
        await self.audit_repo.create(AuditLog(
            user_id=admin_id,
            action="user.suspend",
            entity_type="user",
            entity_id=user_id,
            old_value={"status": old_status},
            new_value={"status": UserStatus.SUSPENDED, "reason": reason},
            ip_address=ip_address
        ))
        return updated_user

    async def update_role(self, user_id: int, admin_id: int, new_role: UserRole, ip_address: str | None = None) -> User:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        old_role = user.role
        user.role = new_role
        updated_user = await self.user_repo.update(user)
        
        await self.audit_repo.create(AuditLog(
            user_id=admin_id,
            action="user.update_role",
            entity_type="user",
            entity_id=user_id,
            old_value={"role": old_role},
            new_value={"role": new_role},
            ip_address=ip_address
        ))
        return updated_user
