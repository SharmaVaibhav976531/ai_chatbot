# backend/app/schemas/chat.py

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.message import MessageRole

class MessageBase(BaseModel):
    """Base schema for messages."""
    model_config = ConfigDict(populate_by_name=True)

    role: MessageRole
    content: str
    metadata_: dict | None = Field(default=None, alias="metadata")

class MessageResponse(MessageBase):
    """Schema for message API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    chat_id: uuid.UUID
    created_at: datetime

class ChatBase(BaseModel):
    """Base schema for chats."""
    title: str = Field(default="New Chat", max_length=255)

class ChatCreate(ChatBase):
    """Schema for creating a chat."""
    pass

class ChatUpdate(BaseModel):
    """Schema for updating a chat."""
    title: str = Field(max_length=255)

class ChatResponse(ChatBase):
    """Schema for chat API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: int
    created_at: datetime
    updated_at: datetime
    
class StreamMessageRequest(BaseModel):
    """Schema for streaming a user message."""
    content: str = Field(..., min_length=1, max_length=10000)
    provider: str = Field(
        default="openai", 
        description="LLM provider to use (openai, anthropic, gemini, ollama)"
    )
    model: str | None = Field(
        default=None, 
        description="Specific model to use. Defaults to provider's standard model."
    )