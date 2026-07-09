# backend/app/services/context.py

import tiktoken
from app.models.message import Message, MessageRole

class ContextManager:
    """Manages conversation context and token limits for LLM prompts."""

    def __init__(self, model: str = "gpt-4o"):
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
        # Safe limit for context window (leaving room for response)
        self.max_tokens = 8000 

    def count_tokens(self, text: str) -> int:
        """Counts the number of tokens in a text string."""
        return len(self.encoding.encode(text))

    def build_context(self, messages: list[Message], system_prompt: str | None = None) -> list[dict]:
        """
        Builds a context window from a list of messages, ensuring it fits within max_tokens.
        Prioritizes recent messages by trimming from the oldest.
        """
        formatted_messages = []
        
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})

        # Format DB messages to OpenAI format
        for msg in messages:
            role = "user" if msg.role == MessageRole.USER else "assistant"
            formatted_messages.append({"role": role, "content": msg.content})

        # Trim from the oldest messages if exceeding token limit
        while self._calculate_total_tokens(formatted_messages) > self.max_tokens and len(formatted_messages) > 1:
            # Keep system prompt (index 0) if it exists, remove the oldest conversation message
            start_idx = 1 if system_prompt else 0
            if len(formatted_messages) > start_idx:
                formatted_messages.pop(start_idx)
            else:
                break

        return formatted_messages

    def _calculate_total_tokens(self, messages: list[dict]) -> int:
        """Calculates total tokens for a list of messages."""
        total = 0
        for msg in messages:
            # Add 4 tokens for message overhead (role, etc.)
            total += self.count_tokens(msg["content"]) + 4
        return total + 2