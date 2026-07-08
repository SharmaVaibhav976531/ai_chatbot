# backend/app/schemas/token.py

from pydantic import BaseModel, ConfigDict

class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """Schema for the decoded JWT payload."""
    sub: str | None = None
    exp: int | None = None
    type: str = "access"

class TokenData(BaseModel):
    """Schema for extracting user ID from token."""
    user_id: int | None = None