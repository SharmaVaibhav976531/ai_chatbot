# backend/app/embeddings/sentence_transformers.py

import asyncio
from sentence_transformers import SentenceTransformer

class SentenceTransformerEmbeddings:
    """Local SentenceTransformers Embeddings implementation."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Model is loaded once and cached
        self.model = SentenceTransformer(model_name)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = await asyncio.to_thread(
            self.model.encode, 
            texts, 
            convert_to_numpy=True, 
            convert_to_tensor=False, 
            show_progress_bar=False
        )
        return embeddings.tolist()

    async def embed_query(self, text: str) -> list[float]:
        embeddings = await asyncio.to_thread(
            self.model.encode, 
            [text], 
            convert_to_numpy=True, 
            convert_to_tensor=False, 
            show_progress_bar=False
        )
        return embeddings[0].tolist()