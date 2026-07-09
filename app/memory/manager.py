# backend/app/memory/manager.py

import json
import redis.asyncio as aioredis
from app.vectorstore.factory import VectorStoreFactory
from app.embeddings.factory import EmbeddingsFactory
from app.core.config import settings

class MemoryManager:
    """Manages short-term, long-term, and vector memory for agents."""

    def __init__(self, redis_client: aioredis.Redis, user_id: int):
        self.redis = redis_client
        self.user_id = user_id
        self.vectorstore = VectorStoreFactory.get_vector_store()
        self.embeddings = EmbeddingsFactory.get_embeddings(settings.EMBEDDINGS_PROVIDER, settings.EMBEDDINGS_MODEL)

    # --- Short Term Memory (Redis) ---
    async def save_short_term(self, key: str, value: str, ttl: int = 3600) -> None:
        """Saves data to short-term memory (Redis) with a TTL."""
        redis_key = f"stm:{self.user_id}:{key}"
        await self.redis.set(redis_key, value, ex=ttl)

    async def get_short_term(self, key: str) -> str | None:
        """Retrieves data from short-term memory."""
        redis_key = f"stm:{self.user_id}:{key}"
        return await self.redis.get(redis_key)

    # --- Long Term Memory (Redis Hash for simplicity, could be Postgres) ---
    async def save_long_term(self, fact_key: str, fact_value: str) -> None:
        """Saves a persistent fact about the user."""
        redis_key = f"ltm:{self.user_id}"
        await self.redis.hset(redis_key, fact_key, fact_value)

    async def get_long_term(self) -> dict:
        """Retrieves all persistent facts about the user."""
        redis_key = f"ltm:{self.user_id}"
        facts = await self.redis.hgetall(redis_key)
        return {k.decode('utf-8'): v.decode('utf-8') for k, v in facts.items()} if facts else {}

    # --- Vector Memory (Semantic Search over past interactions) ---
    async def save_vector_memory(self, interaction_id: str, text: str, metadata: dict) -> None:
        """Saves an interaction to vector memory for semantic retrieval."""
        embedding = await self.embeddings.embed_query(text)
        clean_meta = {**metadata, "user_id": self.user_id, "type": "vector_memory"}
        await self.vectorstore.add_documents(
            ids=[f"mem_{self.user_id}_{interaction_id}"],
            texts=[text],
            embeddings=[embedding],
            metadatas=[clean_meta]
        )

    async def search_vector_memory(self, query: str, top_k: int = 3) -> list[dict]:
        """Searches vector memory for relevant past interactions."""
        query_embedding = await self.embeddings.embed_query(query)
        return await self.vectorstore.search(
            query_embedding, 
            top_k=top_k, 
            filter={"user_id": self.user_id, "type": "vector_memory"}
        )