import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserStatus

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "employee_code": "EMP001",
            "full_name": "Test User",
            "department": "IT"
        }
    )
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["email"] == "test@example.com"
    assert data["status"] == "pending"

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    # First registration
    payload = {
        "email": "dup@example.com",
        "password": "password123",
        "employee_code": "EMP002",
        "full_name": "User 1",
        "department": "IT"
    }
    await client.post("/api/v1/auth/register", json=payload)
    
    # Duplicate registration
    payload["employee_code"] = "EMP003" # Change employee code to test email conflict
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already exists"

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db: AsyncSession):
    # Create active user
    from app.core.security import get_password_hash
    user = User(
        email="active@example.com",
        password_hash=get_password_hash("password123"),
        employee_code="EMP999",
        full_name="Active User",
        department="IT",
        status=UserStatus.ACTIVE
    )
    db.add(user)
    await db.commit()
    
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "active@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "access_token" in data
    assert data["user"]["email"] == "active@example.com"

@pytest.mark.asyncio
async def test_login_pending_user_rejected(client: AsyncClient):
    # Register (defaults to pending)
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "pending@example.com",
            "password": "password123",
            "employee_code": "PEND01",
            "full_name": "Pending User",
            "department": "IT"
        }
    )
    
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "pending@example.com", "password": "password123"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Account is pending approval"

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, db: AsyncSession):
    from app.core.security import get_password_hash
    user = User(
        email="wrongpass@example.com",
        password_hash=get_password_hash("password123"),
        employee_code="WP01",
        full_name="Wrong Pass User",
        department="IT",
        status=UserStatus.ACTIVE
    )
    db.add(user)
    await db.commit()
    
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpass@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
