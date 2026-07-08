# backend/app/services/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.core.security import verify_password, verify_token, create_access_token, create_refresh_token
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RefreshRequest
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse

class AuthService:
    """Service for handling authentication logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def authenticate(self, credentials: LoginRequest) -> Token:
        """Authenticates a user and returns JWT tokens."""
        user = await self.user_repo.get_by_email(credentials.email)
        
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise UnauthorizedException("Incorrect email or password")
            
        if not user.is_active:
            raise UnauthorizedException("Inactive user")

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )

    async def register(self, user_in: UserCreate) -> UserResponse:
        """Registers a new user."""
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise BadRequestException("A user with this email already exists")

        role = await self.user_repo.get_or_create_role(user_in.role_name)
        user = await self.user_repo.create(user_in, role.id)
        
        return UserResponse.model_validate(user)

    async def refresh_tokens(self, refresh_req: RefreshRequest) -> Token:
        """Validates refresh token and issues new tokens."""
        payload = verify_token(refresh_req.refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise UnauthorizedException("Invalid refresh token")

        user = await self.user_repo.get(int(user_id))
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )