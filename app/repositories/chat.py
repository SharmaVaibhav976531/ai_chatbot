# backend/app/repositories/chat.py

import uuid
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat import Chat
from app.schemas.chat import ChatCreate, ChatUpdate
from app.models.message import Message


class ChatRepository:
    """Repository for Chat database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, chat_id: uuid.UUID) -> Chat | None:
        result = await self.session.execute(select(Chat).where(Chat.id == chat_id))
        return result.scalar_one_or_none()

    async def get_user_chats(self, user_id: int, skip: int = 0, limit: int = 50) -> list[Chat]:
        result = await self.session.execute(
            select(Chat)
            .where(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, user_id: int, obj_in: ChatCreate) -> Chat:
        db_obj = Chat(user_id=user_id, title=obj_in.title)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, db_obj: Chat, obj_in: ChatUpdate) -> Chat:
        db_obj.title = obj_in.title
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, chat_id: uuid.UUID) -> bool:
        db_obj = await self.get(chat_id)
        if not db_obj:
            return False
        await self.session.delete(db_obj)
        await self.session.commit()
        return True
    

    
    async def search_chats(self, user_id: int, query: str) -> list[Chat]:
        """Searches chats by title or message content using case-insensitive matching."""
        # Subquery to find chat_ids that contain the query in messages
        msg_subquery = (
            select(Message.chat_id)
            .where(Message.content.ilike(f"%{query}%"))
            .distinct()
        )

        result = await self.session.execute(
            select(Chat)
            .where(
                Chat.user_id == user_id,
                or_(
                    Chat.title.ilike(f"%{query}%"),
                    Chat.id.in_(msg_subquery)
                )
            )
            .order_by(Chat.updated_at.desc())
            .limit(50)
        )
        return list(result.scalars().all())