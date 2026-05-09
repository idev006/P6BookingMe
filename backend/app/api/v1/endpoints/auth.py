from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.user import UserRepository
from app.repositories.audit_log import AuditLogRepository
from app.services.auth import AuthService
from app.core.limiter import limiter
from app.schemas.user import UserCreate, UserResponse, UserLogin, UserUpdate
from app.schemas.auth import Token
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()

def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    user_repo = UserRepository(db)
    audit_repo = AuditLogRepository(db)
    return AuthService(user_repo, audit_repo)

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.register(data, ip_address=request.client.host)
    return {
        "data": UserResponse.model_validate(user).model_dump(mode='json'),
        "message": "สมัครสมาชิกสำเร็จ กรุณารอการอนุมัติจาก Admin"
    }

@router.post("/login", response_model=dict)
@limiter.limit("5/minute")
async def login(
    request: Request,
    data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    token = await auth_service.login(data, ip_address=request.client.host)
    return {
        "data": token.model_dump(mode='json')
    }

@router.get("/me", response_model=dict)
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "data": UserResponse.model_validate(current_user).model_dump(mode='json')
    }

@router.put("/me", response_model=dict)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if data.full_name is not None:
        current_user.full_name = data.full_name
    if data.department is not None:
        current_user.department = data.department
    if data.phone is not None:
        current_user.phone = data.phone
        
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    
    return {
        "data": UserResponse.model_validate(current_user).model_dump(mode='json'),
        "message": "อัปเดตข้อมูลสำเร็จ"
    }

@router.post("/logout", response_model=dict)
async def logout(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
    current_user: User = Depends(get_current_user)
):
    # Get token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"message": "Invalid token format"}
    
    token = auth_header.split(" ")[1]
    await auth_service.blacklist_token(token)
    
    return {"message": "ออกจากระบบสำเร็จ"}
