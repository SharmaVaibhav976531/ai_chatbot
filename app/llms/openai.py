# backend/app/llms/openai.py

import openai
from typing import AsyncGenerator, Any
from app.core.config import settings

class OpenAILLM:
    """Implementation for OpenAI Chat Completions API."""

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def complete(self, messages: list[dict[str, Any]]) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content or ""

    async def stream(self, messages: list[dict[str, Any]]) -> AsyncGenerator[str, None]:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content