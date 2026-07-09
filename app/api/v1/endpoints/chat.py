# backend/app/api/v1/endpoints/chat.py

import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_async_session
from app.api.deps import CurrentUser
from app.schemas.chat import ChatCreate, ChatUpdate, ChatResponse, MessageResponse, MessageBase, StreamMessageRequest
from app.services.chat import ChatService
from fastapi.responses import StreamingResponse
import redis.asyncio as aioredis
from app.database.session import get_async_session
from app.database.redis import get_redis
from app.models.message import MessageRole

router = APIRouter()

@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
async def create_chat(
    chat_in: ChatCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_async_session)]
    ) -> ChatResponse:
    """Creates a new chat conversation."""
    chat_service = ChatService(session)
    return await chat_service.create_chat(current_user.id, chat_in)

@router.get("/", response_model=list[ChatResponse], status_code=status.HTTP_200_OK)
async def list_chats(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
    ) -> list[ChatResponse]:
    """Retrieves a list of chats for the current user."""
    chat_service = ChatService(session)
    return await chat_service.get_user_chats(current_user.id, skip, limit)

@router.get("/{chat_id}", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def get_chat(
    chat_id: uuid.UUID,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_async_session)]
    ) -> ChatResponse:
    """Retrieves a specific chat by ID."""
    chat_service = ChatService(session)
    return await chat_service.get_chat(chat_id, current_user.id)

@router.patch("/{chat_id}", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def update_chat(
    chat_id: uuid.UUID,
    chat_in: ChatUpdate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_async_session)]
    ) -> ChatResponse:
    """Updates a chat's title."""
    chat_service = ChatService(session)
    return await chat_service.update_chat(chat_id, current_user.id, chat_in)

@router.delete("/{chat_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_id: uuid.UUID,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_async_session)]
    ) -> None:
    """Deletes a chat and all its messages."""
    chat_service = ChatService(session)
    await chat_service.delete_chat(chat_id, current_user.id)

@router.get("/{chat_id}/messages", response_model=list[MessageResponse], status_code=status.HTTP_200_OK)
async def list_messages(
    chat_id: uuid.UUID,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
    ) -> list[MessageResponse]:
    """Retrieves message history for a specific chat."""
    chat_service = ChatService(session)
    return await chat_service.get_chat_messages(chat_id, current_user.id, skip, limit)

@router.post("/{chat_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(
    chat_id: uuid.UUID,
    message_in: MessageBase,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_async_session)]
    ) -> MessageResponse:
    """Adds a new message to a chat."""
    chat_service = ChatService(session)
    return await chat_service.add_message(
        chat_id, current_user.id, message_in.role, message_in.content, message_in.metadata_
    )
    
@router.get("/search", response_model=list[ChatResponse], status_code=status.HTTP_200_OK)
async def search_chats(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    q: str = Query(..., min_length=1, description="Search query")
    ) -> list[ChatResponse]:
    """Searches chats by title or message content."""
    chat_service = ChatService(session)
    return await chat_service.search_chats(current_user.id, q)

@router.post("/{chat_id}/messages/stream")
async def stream_message(
    chat_id: uuid.UUID,
    message_in: StreamMessageRequest,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    redis_client: Annotated[aioredis.Redis, Depends(get_redis)]
    ) -> StreamingResponse:
    """Sends a message and streams the assistant's response via Server-Sent Events (SSE)."""
    chat_service = ChatService(session)

    async def event_generator():
        async for chunk in chat_service.stream_message(
            chat_id, current_user.id, message_in.content, redis_client
        ):
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering for real-time streaming
        }
    )