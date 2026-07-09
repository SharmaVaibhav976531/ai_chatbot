# backend/app/tools/factory.py

from app.tools.base import BaseTool
from app.tools.calculator import CalculatorTool
from app.tools.python_exec import PythonExecutionTool
from app.tools.web_search import WebSearchTool
from app.tools.document_search import DocumentSearchTool
from app.tools.datetime_tool import DateTimeTool

class ToolFactory:
    """Factory for creating and managing tool instances."""

    TOOL_MAP = {
        "calculator": CalculatorTool,
        "python_exec": PythonExecutionTool,
        "web_search": WebSearchTool,
        "document_search": DocumentSearchTool,
        "datetime": DateTimeTool,
    }

    @classmethod
    def get_tool(cls, tool_name: str, **kwargs) -> BaseTool:
        tool_class = cls.TOOL_MAP.get(tool_name)
        if not tool_class:
            raise ValueError(f"Unknown tool: {tool_name}")
        return tool_class(**kwargs)

    @classmethod
    def get_tools(cls, tool_names: list[str], **kwargs) -> list[BaseTool]:
        return [cls.get_tool(name, **kwargs) for name in tool_names if name in cls.TOOL_MAP]