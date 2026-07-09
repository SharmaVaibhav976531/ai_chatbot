# backend/app/embeddings/factory.py

from app.embeddings.base import BaseEmbeddings
from app.embeddings.openai import OpenAIEmbeddings
from app.embeddings.sentence_transformers import SentenceTransformerEmbeddings
from app.core.exceptions import BadRequestException

class EmbeddingsFactory:
    """Factory for creating Embeddings instances."""

    PROVIDERS = {
        "openai": OpenAIEmbeddings,
        "sentence_transformers": SentenceTransformerEmbeddings,
    }

    @classmethod
    def get_embeddings(cls, provider: str, model: str | None = None) -> BaseEmbeddings:
        provider = provider.lower()
        if provider not in cls.PROVIDERS:
            raise BadRequestException(f"Unsupported embeddings provider: {provider}. Supported: {list(cls.PROVIDERS.keys())}")
        
        cls_impl = cls.PROVIDERS[provider]
        if model:
            return cls_impl(model=model)
        return cls_impl()