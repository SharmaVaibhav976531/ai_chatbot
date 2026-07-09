# backend/app/schemas/document.py

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.document import DocumentStatus

class DocumentBase(BaseModel):
    """Base schema for documents."""
    filename: str
    file_type: str
    file_size: int

class DocumentResponse(DocumentBase):
    """Schema for document API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: int
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime