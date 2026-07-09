# backend/app/models/message.py

import uuid
import enum
from sqlalchemy import Text, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base, TimestampMixin

class MessageRole(str, enum.Enum):
    """Roles for messages in a conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(Base, TimestampMixin):
    """Represents a single message within a chat."""
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chat_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    
    # Relationships
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages", lazy="noload")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role})>"

from app.models.chat import Chat