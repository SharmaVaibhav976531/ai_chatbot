# backend/app/models/user.py

import enum
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

class UserRoleEnum(str, enum.Enum):
    """Enumeration of available user roles."""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

class User(Base, TimestampMixin):
    """Represents an authenticated user in the system."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    
    # Relationships
    role: Mapped["Role"] = relationship("Role", back_populates="users", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"

from app.models.role import Role