# backend/app/llms/factory.py

from app.llms.base import BaseLLM
from app.llms.openai import OpenAILLM
from app.llms.anthropic import AnthropicLLM
from app.llms.gemini import GeminiLLM
from app.llms.ollama import OllamaLLM
from app.core.exceptions import BadRequestException

class LLMFactory:
    """
    Factory for creating LLM instances.
    Centralizes the mapping of provider strings to their respective implementations.
    """

    PROVIDERS = {
        "openai": OpenAILLM,
        "anthropic": AnthropicLLM,
        "gemini": GeminiLLM,
        "ollama": OllamaLLM,
    }

    DEFAULT_MODELS = {
        "openai": "gpt-3.5-turbo",
        "anthropic": "claude-3-haiku-20240307",
        "gemini": "gemini-pro",
        "ollama": "llama3"
    }

    @classmethod
    def get_llm(cls, provider: str, model: str | None = None) -> BaseLLM:
        """
        Retrieves an instance of the requested LLM provider.
        
        Args:
            provider: The name of the provider (e.g., 'openai', 'anthropic').
            model: Optional specific model name. Falls back to default if not provided.
            
        Returns:
            An instance of the requested LLM implementing BaseLLM.
            
        Raises:
            BadRequestException: If the provider is not supported.
        """
        provider = provider.lower()
        if provider not in cls.PROVIDERS:
            raise BadRequestException(f"Unsupported LLM provider: {provider}. Supported: {list(cls.PROVIDERS.keys())}")
        
        llm_class = cls.PROVIDERS[provider]
        selected_model = model or cls.DEFAULT_MODELS.get(provider)
        
        return llm_class(model=selected_model)