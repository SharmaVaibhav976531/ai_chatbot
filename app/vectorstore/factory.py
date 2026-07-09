# backend/app/vectorstore/factory.py

from app.vectorstore.base import BaseVectorStore
from app.vectorstore.chroma import ChromaVectorStore
from app.vectorstore.faiss import FAISSVectorStore
from app.vectorstore.pinecone import PineconeVectorStore
from app.core.config import settings
from app.core.exceptions import BadRequestException

class VectorStoreFactory:
    """Factory for creating Vector Store instances."""

    @classmethod
    def get_vector_store(cls, provider: str | None = None) -> BaseVectorStore:
        """
        Retrieves an instance of the requested Vector Store provider.
        
        Args:
            provider: The name of the provider. Defaults to settings.VECTOR_DB_PROVIDER.
            
        Returns:
            An instance of the requested Vector Store implementing BaseVectorStore.
        """
        provider = (provider or settings.VECTOR_DB_PROVIDER).lower()
        
        if provider == "chroma":
            return ChromaVectorStore()
        elif provider == "faiss":
            return FAISSVectorStore()
        elif provider == "pinecone":
            if not settings.PINECONE_API_KEY:
                raise BadRequestException("Pinecone API key is not configured")
            return PineconeVectorStore(
                api_key=settings.PINECONE_API_KEY,
                index_name=settings.PINECONE_INDEX_NAME,
                environment=settings.PINECONE_ENVIRONMENT
            )
        else:
            raise BadRequestException(f"Unsupported vector store provider: {provider}. Supported: chroma, faiss, pinecone")