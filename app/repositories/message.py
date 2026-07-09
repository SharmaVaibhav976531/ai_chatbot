# backend/app/repositories/message.py

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message, MessageRole

class MessageRepository:
    """Repository for Message database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_chat_messages(self, chat_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[Message]:
        result = await self.session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, chat_id: uuid.UUID, role: MessageRole, content: str, metadata_: dict | None = None) -> Message:
        db_obj = Message(chat_id=chat_id, role=role, content=content, metadata_=metadata_)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj