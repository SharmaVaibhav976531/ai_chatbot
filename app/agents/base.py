# backend/app/agents/base.py

from typing import Any
from app.tools.base import BaseTool

class BaseAgent:
    """Base class for all specialized AI agents."""
    
    name: str
    description: str
    system_prompt: str
    tools: list[BaseTool]

    def __init__(self, tools: list[BaseTool] | None = None):
        self.tools = tools or []

    def get_tool_descriptions(self) -> str:
        """Formats tool descriptions for the LLM prompt."""
        if not self.tools:
            return "No tools available."
        return "\n".join([f"- {t.name}: {t.description}" for t in self.tools])