# backend/app/models/chat.py

import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

class Chat(Base, TimestampMixin):
    """Represents a conversation thread."""
    __tablename__ = "chats"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="New Chat")
    
    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="chat", cascade="all, delete-orphan", lazy="noload"
    )
    user: Mapped["User"] = relationship("User", lazy="noload")

    def __repr__(self) -> str:
        return f"<Chat(id={self.id}, title={self.title})>"

from app.models.user import User
from app.models.message import Message