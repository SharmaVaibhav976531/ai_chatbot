# backend/app/repositories/user.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate

class UserRepository:
    """Repository for User database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int) -> User | None:
        """Retrieves a user by ID."""
        result = await self.session.execute(
            select(User).options(selectinload(User.role)).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Retrieves a user by email."""
        result = await self.session.execute(
            select(User).options(selectinload(User.role)).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_multi(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Retrieves a list of users."""
        result = await self.session.execute(
            select(User).options(selectinload(User.role)).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, obj_in: UserCreate, role_id: int) -> User:
        """Creates a new user."""
        from app.core.security import get_password_hash
        
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            role_id=role_id,
            is_active=True,
            is_superuser=(obj_in.role_name == "admin")
        )
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: User, obj_in: UserUpdate) -> User:
        """Updates an existing user."""
        update_data = obj_in.model_dump(exclude_unset=True)
        
        if "password" in update_data:
            from app.core.security import get_password_hash
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get_or_create_role(self, role_name: str) -> Role:
        """Gets a role by name or creates it if it doesn't exist."""
        result = await self.session.execute(select(Role).where(Role.name == role_name))
        role = result.scalar_one_or_none()
        
        if not role:
            role = Role(name=role_name, description=f"Default {role_name} role")
            self.session.add(role)
            await self.session.commit()
            await self.session.refresh(role)
            
        return role