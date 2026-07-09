# backend/app/llms/ollama.py

import ollama
from typing import AsyncGenerator, Any
from app.core.config import settings

class OllamaLLM:
    """Implementation for local Ollama models."""

    def __init__(self, model: str = "llama3"):
        self.model = model
        self.client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)

    async def complete(self, messages: list[dict[str, Any]]) -> str:
        response = await self.client.chat(model=self.model, messages=messages)
        return response['message']['content']

    async def stream(self, messages: list[dict[str, Any]]) -> AsyncGenerator[str, None]:
        response = await self.client.chat(model=self.model, messages=messages, stream=True)
        async for chunk in response:
            if chunk['message']['content']:
                yield chunk['message']['content']