# backend/app/embeddings/base.py

from typing import Protocol

class BaseEmbeddings(Protocol):
    """Protocol for embedding providers."""

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embeds a list of documents."""
        ...

    async def embed_query(self, text: str) -> list[float]:
        """Embeds a single query string."""
        ...