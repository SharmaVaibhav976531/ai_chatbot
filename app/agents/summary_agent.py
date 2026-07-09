# backend/app/agents/summary_agent.py

from app.agents.base import BaseAgent
from app.prompts.templates import PromptTemplates

class SummaryAgent(BaseAgent):
    """Agent specialized in summarizing long texts."""
    name = "summary"
    description = "Handles requests to summarize long texts, articles, or documents."
    system_prompt = PromptTemplates.SUMMARY

    def __init__(self, **kwargs):
        super().__init__(tools=[], **kwargs) # No tools needed, pure LLM task