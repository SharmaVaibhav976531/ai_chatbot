# backend/app/api/deps.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_async_session

from typing import Annotated, Callable
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_session
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import verify_token
from app.models.user import User
from app.repositories.user import UserRepository

__all__ = ["get_async_session"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> User:
    """Dependency to extract and validate the current user from the JWT."""
    credentials_exception = UnauthorizedException("Could not validate credentials")
    
    payload = verify_token(token, token_type="access")
    user_id: str | None = payload.get("sub")
    
    if user_id is None:
        raise credentials_exception

    user_repo = UserRepository(session)
    user = await user_repo.get(int(user_id))
    
    if user is None:
        raise credentials_exception
        
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Dependency to ensure the current user is active."""
    if not current_user.is_active:
        raise UnauthorizedException("Inactive user")
    return current_user

def require_role(allowed_roles: list[str]) -> Callable:
    """Dependency factory to enforce Role-Based Access Control (RBAC)."""
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)]
    ) -> User:
        if current_user.role.name not in allowed_roles and not current_user.is_superuser:
            raise ForbiddenException("Not authorized to perform this action")
        return current_user
    return role_checker

# Convenience dependencies
CurrentUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(require_role(["admin"]))]
ModeratorUser = Annotated[User, Depends(require_role(["admin", "moderator"]))]