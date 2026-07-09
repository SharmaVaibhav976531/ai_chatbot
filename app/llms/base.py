# backend/app/llms/base.py

from typing import Protocol, AsyncGenerator, Any

class BaseLLM(Protocol):
    """
    Protocol defining the standard interface for all LLM providers.
    Ensures that all implementations support both synchronous completion 
    and asynchronous streaming.
    """

    async def complete(self, messages: list[dict[str, Any]]) -> str:
        """
        Generates a complete, non-streaming response from the LLM.
        
        Args:
            messages: A list of message dictionaries in the standard format:
                      [{"role": "system|user|assistant", "content": "..."}]
        Returns:
            The full text response from the LLM.
        """
        ...

    async def stream(self, messages: list[dict[str, Any]]) -> AsyncGenerator[str, None]:
        """
        Streams a response from the LLM chunk by chunk.
        
        Args:
            messages: A list of message dictionaries in the standard format.
        Yields:
            String chunks of the generated text.
        """
        ...