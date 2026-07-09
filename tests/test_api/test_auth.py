# backend/tests/test_api/test_auth.py

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRoleEnum
from app.models.role import Role
from app.core.security import get_password_hash

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, db_session: AsyncSession):
    # Setup role
    role = Role(name="user", description="Standard user")
    db_session.add(role)
    await db_session.commit()

    response = await client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "password": "securepassword123",
        "full_name": "Test User",
        "role_name": "user"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, db_session: AsyncSession):
    # Setup user
    role = Role(name="user", description="Standard user")
    db_session.add(role)
    await db_session.flush()
    
    user = User(
        email="login@example.com",
        hashed_password=get_password_hash("password123"),
        role_id=role.id,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"