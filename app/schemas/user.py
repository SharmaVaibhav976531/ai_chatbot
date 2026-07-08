# backend/app/schemas/user.py

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserBase(BaseModel):
    """Base schema for User."""
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=100)

class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=128)
    role_name: str = Field(default="user", description="Role to assign (admin, moderator, user)")

class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = None

class UserResponse(UserBase):
    """Schema for user API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    role_name: str
    created_at: datetime

class UserInDB(UserResponse):
    """Internal schema including sensitive fields."""
    hashed_password: str