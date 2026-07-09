# backend/app/embeddings/openai.py

import openai
from app.core.config import settings

class OpenAIEmbeddings:
    """OpenAI Embeddings implementation."""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = await self.client.embeddings.create(input=texts, model=self.model)
        return [item.embedding for item in response.data]

    async def embed_query(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(input=[text], model=self.model)
        return response.data[0].embedding