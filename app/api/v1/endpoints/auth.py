# backend/app/api/v1/endpoints/auth.py

from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_session
from app.schemas.auth import LoginRequest, RefreshRequest
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.services.auth import AuthService

router = APIRouter()

@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    credentials: LoginRequest, 
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> Token:
    """Authenticates a user and returns access and refresh tokens."""
    auth_service = AuthService(session)
    return await auth_service.authenticate(credentials)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate, 
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> UserResponse:
    """Registers a new user in the system."""
    auth_service = AuthService(session)
    return await auth_service.register(user_in)

@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_req: RefreshRequest, 
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> Token:
    """Refreshes the access token using a valid refresh token."""
    auth_service = AuthService(session)
    return await auth_service.refresh_tokens(refresh_req)