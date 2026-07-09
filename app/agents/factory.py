# backend/app/agents/factory.py

from app.agents.base import BaseAgent
from app.agents.chat_agent import ChatAgent
from app.agents.knowledge_agent import KnowledgeAgent
from app.agents.search_agent import SearchAgent
from app.agents.document_agent import DocumentAgent
from app.agents.summary_agent import SummaryAgent
from app.core.exceptions import BadRequestException

class AgentFactory:
    """Factory for creating specialized AI agents."""

    AGENT_MAP = {
        "chat": ChatAgent,
        "knowledge": KnowledgeAgent,
        "search": SearchAgent,
        "document": DocumentAgent,
        "summary": SummaryAgent,
    }

    @classmethod
    def get_agent(cls, agent_name: str, user_id: int) -> BaseAgent:
        agent_class = cls.AGENT_MAP.get(agent_name)
        if not agent_class:
            raise BadRequestException(f"Unknown agent: {agent_name}. Supported: {list(cls.AGENT_MAP.keys())}")
        
        # Inject user_id for agents that need it (Knowledge, Document)
        if agent_name in ["knowledge", "document"]:
            return agent_class(user_id=user_id)
        
        return agent_class()