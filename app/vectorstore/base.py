# backend/app/vectorstore/base.py

from typing import Protocol, Any

class BaseVectorStore(Protocol):
    """Protocol for Vector Database operations."""

    async def add_documents(self, ids: list[str], texts: list[str], embeddings: list[list[float]], metadatas: list[dict]) -> None:
        """Adds documents and their embeddings to the vector store."""
        ...

    async def search(self, query_embedding: list[float], top_k: int = 5, filter: dict | None = None) -> list[dict[str, Any]]:
        """Searches for the most similar documents."""
        ...

    async def delete(self, ids: list[str]) -> None:
        """Deletes documents from the vector store by ID."""
        ...