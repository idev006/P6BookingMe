import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserStatus, UserRole
from app.core.security import get_password_hash, create_access_token

@pytest.fixture
async def admin_token(db: AsyncSession) -> str:
    admin = User(
        email="admin_test@example.com",
        password_hash=get_password_hash("password123"),
        employee_code="ADM001",
        full_name="Admin",
        department="IT",
        status=UserStatus.ACTIVE,
        role=UserRole.ADMIN
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return create_access_token(admin.id)

@pytest.fixture
async def member_token(db: AsyncSession) -> str:
    member = User(
        email="member_test@example.com",
        password_hash=get_password_hash("password123"),
        employee_code="MEM001",
        full_name="Member",
        department="IT",
        status=UserStatus.ACTIVE,
        role=UserRole.MEMBER
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return create_access_token(member.id)

@pytest.mark.asyncio
async def test_admin_approve_user(client: AsyncClient, db: AsyncSession, admin_token: str):
    # Create a pending user
    user = User(
        email="to_approve@example.com",
        password_hash="...",
        employee_code="APP01",
        full_name="To Approve",
        department="IT",
        status=UserStatus.PENDING
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    response = await client.post(
        f"/api/v1/admin/users/{user.id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "อนุมัติ" in response.json()["message"]
    
    # Check DB
    await db.refresh(user)
    assert user.status == UserStatus.ACTIVE

@pytest.mark.asyncio
async def test_non_admin_cannot_approve(client: AsyncClient, db: AsyncSession, member_token: str):
    user = User(
        email="to_approve2@example.com",
        password_hash="...",
        employee_code="APP02",
        full_name="To Approve 2",
        department="IT",
        status=UserStatus.PENDING
    )
    db.add(user)
    await db.commit()
    
    response = await client.post(
        f"/api/v1/admin/users/{user.id}/approve",
        headers={"Authorization": f"Bearer {member_token}"}
    )
    assert response.status_code == 403
    assert "Admin" in response.json()["detail"]
