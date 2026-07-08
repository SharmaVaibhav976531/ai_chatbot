# backend/app/models/role.py

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

class Role(Base, TimestampMixin):
    """Represents a user role for Role-Based Access Control (RBAC)."""
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationship to users
    users: Mapped[list["User"]] = relationship("User", back_populates="role", lazy="noload")

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name})>"

# Import User here to avoid circular imports at runtime if needed, 
# but SQLAlchemy handles string references in relationships well.
from app.models.user import User