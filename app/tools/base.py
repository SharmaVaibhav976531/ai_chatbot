# backend/app/tools/base.py

from typing import Protocol, Any

class BaseTool(Protocol):
    """Protocol for all executable tools."""
    
    name: str
    description: str

    async def run(self, input_data: str) -> str:
        """Executes the tool with the given input and returns a string result."""
        ...