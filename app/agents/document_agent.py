# backend/app/agents/search_agent.py

from app.agents.base import BaseAgent
from app.prompts.templates import PromptTemplates
from app.tools.web_search import WebSearchTool

class SearchAgent(BaseAgent):
    """Agent specialized in real-time web search."""
    name = "search"
    description = "Handles queries requiring real-time information from the internet."
    system_prompt = PromptTemplates.SYSTEM + "\n\nYou have access to web search. Use it to find current information."

    def __init__(self, **kwargs):
        super().__init__(tools=[WebSearchTool()], **kwargs)