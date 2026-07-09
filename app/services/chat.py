# backend/app/services/chat.py
import uuid
import json
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis
from datetime import datetime, timezone
from app.core.exceptions import NotFoundException, ForbiddenException, BadRequestException
from app.repositories.chat import ChatRepository
from app.repositories.message import MessageRepository
from app.schemas.chat import ChatCreate, ChatUpdate, ChatResponse, MessageResponse
from app.models.message import MessageRole
from app.services.context import ContextManager
from app.services.session import SessionManager
from app.llms.factory import LLMFactory
from langchain_core.messages import HumanMessage
from app.langgraph.graph import compiled_graph

class ChatService:
    """Service for handling chat and message business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.chat_repo = ChatRepository(session)
        self.message_repo = MessageRepository(session)

    async def create_chat(self, user_id: int, chat_in: ChatCreate) -> ChatResponse:
        chat = await self.chat_repo.create(user_id, chat_in)
        return ChatResponse.model_validate(chat)

    async def get_user_chats(self, user_id: int, skip: int, limit: int) -> list[ChatResponse]:
        chats = await self.chat_repo.get_user_chats(user_id, skip, limit)
        return [ChatResponse.model_validate(c) for c in chats]

    async def get_chat(self, chat_id: uuid.UUID, user_id: int) -> ChatResponse:
        chat = await self.chat_repo.get(chat_id)
        if not chat:
            raise NotFoundException("Chat not found")
        if chat.user_id != user_id:
            raise ForbiddenException("Not authorized to access this chat")
        return ChatResponse.model_validate(chat)

    async def update_chat(self, chat_id: uuid.UUID, user_id: int, chat_in: ChatUpdate) -> ChatResponse:
        await self.get_chat(chat_id, user_id) # Validates existence and ownership
        db_chat = await self.chat_repo.get(chat_id)
        updated_chat = await self.chat_repo.update(db_chat, chat_in)
        return ChatResponse.model_validate(updated_chat)

    async def delete_chat(self, chat_id: uuid.UUID, user_id: int) -> bool:
        await self.get_chat(chat_id, user_id) # Validates existence and ownership
        return await self.chat_repo.delete(chat_id)

    async def get_chat_messages(self, chat_id: uuid.UUID, user_id: int, skip: int, limit: int) -> list[MessageResponse]:
        await self.get_chat(chat_id, user_id) # Validates existence and ownership
        messages = await self.message_repo.get_chat_messages(chat_id, skip, limit)
        return [MessageResponse.model_validate(m) for m in messages]

    async def add_message(self, chat_id: uuid.UUID, user_id: int, role: MessageRole, content: str, metadata_: dict | None = None) -> MessageResponse:
        await self.get_chat(chat_id, user_id) # Validates existence and ownership
        message = await self.message_repo.create(chat_id, role, content, metadata_)
        
        # Bump the chat's updated_at timestamp so it appears at the top of the list
        chat = await self.chat_repo.get(chat_id)
        if chat:
            chat.updated_at = datetime.now(timezone.utc)
            self.session.add(chat)
            await self.session.commit()
            
        return MessageResponse.model_validate(message)
    
    async def search_chats(self, user_id: int, query: str) -> list[ChatResponse]:
        """Searches chats by title or message content."""
        chats = await self.chat_repo.search_chats(user_id, query)
        return [ChatResponse.model_validate(c) for c in chats]

    async def stream_message(
        self, chat_id: uuid.UUID, user_id: int, content: str, 
        provider: str, model: str | None, redis_client: aioredis.Redis
    ) -> AsyncGenerator[str, None]:
        """Processes a user message using the LangGraph workflow and streams the response."""
        session_mgr = SessionManager(redis_client)
        
        await session_mgr.acquire_lock(chat_id)
        
        try:
            # 1. Save user message
            await self.add_message(chat_id, user_id, MessageRole.USER, content)
            
            # 2. Auto-title if first message
            messages = await self.message_repo.get_chat_messages(chat_id, limit=2)
            if len(messages) == 1:
                await self._auto_title_chat(chat_id, content)
            
            # 3. Get full history for context
            all_messages = await self.message_repo.get_chat_messages(chat_id, limit=100)
            context_mgr = ContextManager()
            
            # Convert DB messages to LangChain messages for the graph
            lc_messages = []
            for msg in all_messages:
                if msg.role == MessageRole.USER:
                    lc_messages.append(HumanMessage(content=msg.content))
                elif msg.role == MessageRole.ASSISTANT:
                    lc_messages.append(AIMessage(content=msg.content))
                elif msg.role == MessageRole.SYSTEM:
                    lc_messages.append(SystemMessage(content=msg.content))

            # 4. Prepare initial state for LangGraph
            initial_state = {
                "messages": lc_messages,
                "user_id": user_id,
                "chat_id": str(chat_id),
                "provider": provider,
                "model": model,
                "retrieved_context": "",
                "next_action": "direct",
                "tool_calls": [],
                "final_response": ""
            }

            # 5. Invoke the LangGraph workflow
            # Note: For true streaming from LangGraph, we would use `astream_events`.
            # Here we invoke synchronously and stream the final result to maintain 
            # compatibility with our existing SSE implementation.
            final_state = compiled_graph.invoke(initial_state)
            
            assistant_content = final_state.get("final_response", "No response generated.")
            
            # Simulate streaming for the client (In a full implementation, 
            # you would use LangGraph's astream_events to stream token-by-token)
            words = assistant_content.split(" ")
            for i in range(0, len(words), 3):
                chunk = " ".join(words[i:i+3]) + " "
                yield f"data: {json.dumps({'content': chunk})}\n\n"
                await asyncio.sleep(0.05) # Simulate network delay
            
            # 6. Save assistant message
            await self.add_message(chat_id, user_id, MessageRole.ASSISTANT, assistant_content)
            
            # 7. Send completion event
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        finally:
            await session_mgr.release_lock(chat_id)

    async def _auto_title_chat(self, chat_id: uuid.UUID, first_message: str) -> None:
        """Generates a title for the chat based on the first message."""
        title = first_message[:50].strip()
        if len(first_message) > 50:
            title += "..."
        
        chat = await self.chat_repo.get(chat_id)
        if chat:
            await self.chat_repo.update(chat, ChatUpdate(title=title))
