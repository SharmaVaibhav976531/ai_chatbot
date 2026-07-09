# backend/app/vectorstore/pinecone.py

import asyncio
from typing import Any
from pinecone import Pinecone, ServerlessSpec
from app.core.config import settings
from app.core.exceptions import BadRequestException

class PineconeVectorStore:
    """Pinecone implementation of the Vector Store."""

    def __init__(self, api_key: str, index_name: str, environment: str = "us-east-1", dimension: int = 1536):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.dimension = dimension
        
        # Initialize index in a background thread to avoid blocking startup
        asyncio.create_task(self._ensure_index_exists(environment))

    async def _ensure_index_exists(self, environment: str) -> None:
        """Creates the Pinecone index if it doesn't already exist."""
        def _create():
            existing_indexes = self.pc.list_indexes().names()
            if self.index_name not in existing_indexes:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region=environment)
                )
        
        try:
            await asyncio.to_thread(_create)
        except Exception as e:
            # Log error but don't crash the app; it might be a permissions issue or index already exists
            import structlog
            structlog.get_logger().error("pinecone_index_creation_failed", error=str(e))

    def _get_index(self):
        return self.pc.Index(self.index_name)

    async def add_documents(
        self, ids: list[str], texts: list[str], embeddings: list[list[float]], metadatas: list[dict]
    ) -> None:
        if not ids: return

        # Pinecone requires metadata values to be string, number, or boolean
        clean_metadatas = []
        for meta in metadatas:
            clean_meta = {k: v for k, v in meta.items() if isinstance(v, (str, int, float, bool))}
            clean_metadatas.append(clean_meta)

        upsert_data = [
            {"id": id_, "values": emb, "metadata": {**meta, "content": text}}
            for id_, emb, meta, text in zip(ids, embeddings, clean_metadatas, texts)
        ]

        def _upsert():
            index = self._get_index()
            # Pinecone has a batch limit, usually 100 or 2000 depending on payload size
            batch_size = 100
            for i in range(0, len(upsert_data), batch_size):
                index.upsert(vectors=upsert_data[i:i + batch_size])

        await asyncio.to_thread(_upsert)

    async def search(
        self, query_embedding: list[float], top_k: int = 5, filter: dict | None = None
    ) -> list[dict[str, Any]]:
        def _query():
            index = self._get_index()
            kwargs = {"vector": query_embedding, "top_k": top_k, "include_metadata": True}
            if filter:
                kwargs["filter"] = filter
            return index.query(**kwargs)

        results = await asyncio.to_thread(_query)
        
        formatted = []
        for match in results.get("matches", []):
            metadata = match.get("metadata", {})
            content = metadata.pop("content", "")
            formatted.append({
                "id": match["id"],
                "content": content,
                "metadata": metadata,
                "score": match.get("score", 0.0)
            })
        return formatted

    async def delete(self, ids: list[str]) -> None:
        if not ids: return

        def _delete():
            index = self._get_index()
            # Pinecone delete supports batch
            batch_size = 100
            for i in range(0, len(ids), batch_size):
                index.delete(ids=ids[i:i + batch_size])

        await asyncio.to_thread(_delete)