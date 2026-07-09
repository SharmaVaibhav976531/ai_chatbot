# backend/app/embeddings/__init__.py

from app.embeddings.base import BaseEmbeddings
from app.embeddings.factory import EmbeddingsFactory

__all__ = ["BaseEmbeddings", "EmbeddingsFactory"]