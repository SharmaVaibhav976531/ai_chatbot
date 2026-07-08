# backend/app/services/user.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundException
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse, UserUpdate

class UserService:
    """Service for handling user management logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def get_profile(self, user_id: int) -> UserResponse:
        """Retrieves a user's profile."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException("User not found")
        
        # Map role name to response
        response_data = UserResponse.model_validate(user)
        response_data.role_name = user.role.name
        return response_data

    async def update_profile(self, user_id: int, user_in: UserUpdate) -> UserResponse:
        """Updates a user's profile."""
        user = await self.user_repo.get(user_id)
        if not user:
            raise NotFoundException("User not found")

        updated_user = await self.user_repo.update(user, user_in)
        
        response_data = UserResponse.model_validate(updated_user)
        response_data.role_name = updated_user.role.name
        return response_data

    async def get_all_users(self, skip: int, limit: int) -> list[UserResponse]:
        """Retrieves all users (Admin only)."""
        users = await self.user_repo.get_multi(skip=skip, limit=limit)
        return [
            UserResponse(
                id=u.id, email=u.email, full_name=u.full_name, 
                is_active=u.is_active, role_name=u.role.name, created_at=u.created_at
            ) for u in users
        ]