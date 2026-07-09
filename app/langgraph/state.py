# backend/app/langgraph/state.py

from typing import Annotated, Any, Literal
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """Defines the state schema for the AI Workflow graph."""
    messages: Annotated[list[BaseMessage], add_messages]
    
    user_id: int
    chat_id: str
    provider: str
    model: str | None
    
    # Agent & Routing
    selected_agent: str  # New: Tracks which agent is handling the request
    next_action: Literal["direct", "rag", "tool", "agent"]
    
    # RAG & Tools
    retrieved_context: str
    
    # Routing & Execution
    next_action: Literal["direct", "rag", "tool"]
    tool_calls: list[dict[str, Any]]
    
    # Final Output
    final_response: str