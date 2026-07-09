# backend/app/llms/anthropic.py

import anthropic
from typing import AsyncGenerator, Any
from app.core.config import settings

class AnthropicLLM:
    """Implementation for Anthropic Claude Messages API."""

    def __init__(self, model: str = "claude-3-haiku-20240307"):
        self.model = model
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    def _format_messages(self, messages: list[dict[str, Any]]) -> tuple[str | None, list[dict]]:
        """
        Anthropic requires the system prompt to be passed as a separate parameter,
        not within the messages array.
        """
        system_msg = None
        formatted = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                formatted.append({"role": msg["role"], "content": msg["content"]})
        return system_msg, formatted

    async def complete(self, messages: list[dict[str, Any]]) -> str:
        system, fmt_msgs = self._format_messages(messages)
        kwargs: dict[str, Any] = {"model": self.model, "max_tokens": 1024, "messages": fmt_msgs}
        if system:
            kwargs["system"] = system
            
        response = await self.client.messages.create(**kwargs)
        return response.content[0].text

    async def stream(self, messages: list[dict[str, Any]]) -> AsyncGenerator[str, None]:
        system, fmt_msgs = self._format_messages(messages)
        kwargs: dict[str, Any] = {"model": self.model, "max_tokens": 1024, "messages": fmt_msgs}
        if system:
            kwargs["system"] = system
            
        async with self.client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                yield text