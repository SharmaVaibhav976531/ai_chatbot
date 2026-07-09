# backend/app/agents/knowledge_agent.py

from app.agents.base import BaseAgent
from app.prompts.templates import PromptTemplates
from app.tools.document_search import DocumentSearchTool

class KnowledgeAgent(BaseAgent):
    """Agent specialized in RAG and internal knowledge retrieval."""
    name = "knowledge"
    description = "Handles questions about uploaded documents and internal knowledge base."
    system_prompt = PromptTemplates.RAG

    def __init__(self, user_id: int, **kwargs):
        super().__init__(tools=[DocumentSearchTool(user_id=user_id)], **kwargs)