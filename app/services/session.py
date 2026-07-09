# backend/app/services/session.py

import uuid
import redis.asyncio as aioredis
from app.core.exceptions import BadRequestException

class SessionManager:
    """Manages active chat sessions using Redis distributed locks."""

    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.lock_prefix = "chat_lock:"
        self.lock_ttl = 60  # seconds

    async def acquire_lock(self, chat_id: uuid.UUID) -> bool:
        """Acquires a distributed lock for a chat session."""
        lock_key = f"{self.lock_prefix}{chat_id}"
        # SETNX with TTL
        acquired = await self.redis.set(lock_key, "1", nx=True, ex=self.lock_ttl)
        if not acquired:
            raise BadRequestException("Chat is currently being processed. Please wait.")
        return True

    async def release_lock(self, chat_id: uuid.UUID) -> None:
        """Releases the distributed lock for a chat session."""
        lock_key = f"{self.lock_prefix}{chat_id}"
        await self.redis.delete(lock_key)