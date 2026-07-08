# backend/app/schemas/auth.py

from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str