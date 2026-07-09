# backend/app/models/document_chunk.py

import uuid
from sqlalchemy import Integer, ForeignKey, Text, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class DocumentChunk(Base):
    """Represents a chunk of a document, linked to a vector ID."""
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    vector_id: Mapped[str | None] = mapped_column(String(255), nullable=True) # Reference to Vector DB
    
    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks", lazy="noload")

from app.models.document import Document