# backend/app/api/v1/endpoints/users.py

from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_session
from app.api.deps import CurrentUser, AdminUser
from app.schemas.user import UserResponse, UserUpdate
from app.services.user import UserService

router = APIRouter()

@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def read_current_user(
    current_user: CurrentUser
) -> UserResponse:
    """Retrieves the profile of the currently authenticated user."""
    # We reconstruct the response to include the role name cleanly
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        role_name=current_user.role.name,
        created_at=current_user.created_at
    )

@router.patch("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def update_current_user(
    user_in: UserUpdate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> UserResponse:
    """Updates the profile of the currently authenticated user."""
    user_service = UserService(session)
    return await user_service.update_profile(current_user.id, user_in)

@router.get("/", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
async def read_users(
    admin_user: AdminUser,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> list[UserResponse]:
    """Retrieves all users. Restricted to Admins."""
    user_service = UserService(session)
    return await user_service.get_all_users(skip=skip, limit=limit)