from fastapi import HTTPException, status
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User, UserStatus
from app.repositories.user import UserRepository
from app.repositories.audit_log import AuditLogRepository
from app.models.audit_log import AuditLog
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.auth import Token
from app.core.config import settings

class AuthService:
    def __init__(self, user_repo: UserRepository, audit_repo: AuditLogRepository):
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    async def register(self, data: UserCreate, ip_address: str | None = None) -> User:
        if await self.user_repo.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
                headers={"X-Error-Code": "DUPLICATE_EMAIL"}
            )
        if await self.user_repo.get_by_employee_code(data.employee_code):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee code already exists",
                headers={"X-Error-Code": "DUPLICATE_EMPLOYEE_CODE"}
            )
            
        new_user = User(
            email=data.email,
            password_hash=get_password_hash(data.password),
            employee_code=data.employee_code,
            full_name=data.full_name,
            department=data.department,
            phone=data.phone,
            status=UserStatus.PENDING
        )
        user = await self.user_repo.create(new_user)

        # บันทึก Audit Log สำหรับการสมัครสมาชิก
        audit_entry = AuditLog(
            user_id=user.id,
            action="user.register",
            entity_type="user",
            entity_id=user.id,
            new_value={
                "email": user.email,
                "full_name": user.full_name,
                "employee_code": user.employee_code
            },
            ip_address=ip_address
        )
        await self.audit_repo.create(audit_entry)
        
        return user

    async def login(self, data: UserLogin, ip_address: str | None = None) -> Token:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            # บันทึก Audit Log สำหรับการเข้าสู่ระบบไม่สำเร็จ
            await self.audit_repo.create(AuditLog(
                user_id=user.id if user else None,
                action="user.login_failed",
                entity_type="user",
                entity_id=user.id if user else 0,
                new_value={"email": data.email},
                ip_address=ip_address
            ))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
            
        if user.status == UserStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is pending approval",
                headers={"X-Error-Code": "ACCOUNT_PENDING"}
            )
        if user.status == UserStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is suspended",
                headers={"X-Error-Code": "ACCOUNT_SUSPENDED"}
            )
        if user.status == UserStatus.REJECTED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account registration was rejected",
                headers={"X-Error-Code": "ACCOUNT_REJECTED"}
            )
        if user.status == UserStatus.DELETED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deleted"
            )
            
        access_token = create_access_token(subject=user.id)
        
        # บันทึก Audit Log สำหรับการเข้าสู่ระบบสำเร็จ
        audit_entry = AuditLog(
            user_id=user.id,
            action="user.login",
            entity_type="user",
            entity_id=user.id,
            ip_address=ip_address
        )
        await self.audit_repo.create(audit_entry)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user
        )

    async def blacklist_token(self, token: str):
        from app.models.token_blacklist import TokenBlacklist
        from jose import jwt
        from datetime import datetime, UTC, timedelta
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            exp = payload.get("exp")
            expires_at = datetime.fromtimestamp(exp, tz=UTC) if exp else datetime.now(UTC) + timedelta(hours=1)
            
            # Check if already blacklisted to avoid duplicate error
            from sqlalchemy import select
            stmt = select(TokenBlacklist).where(TokenBlacklist.token == token)
            res = await self.user_repo.session.execute(stmt)
            if res.scalars().first():
                return
                
            blacklist_item = TokenBlacklist(token=token, expires_at=expires_at)
            self.user_repo.session.add(blacklist_item)
            await self.user_repo.session.commit()
        except Exception as e:
            # If token is invalid/expired, we don't need to blacklist it
            pass
