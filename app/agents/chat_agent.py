# backend/app/agents/chat_agent.py

from app.agents.base import BaseAgent
from app.prompts.templates import PromptTemplates
from app.tools.datetime_tool import DateTimeTool

class ChatAgent(BaseAgent):
    """General conversational agent."""
    name = "chat"
    description = "Handles general conversation, greetings, and casual queries."
    system_prompt = PromptTemplates.CHAT

    def __init__(self, **kwargs):
        super().__init__(tools=[DateTimeTool()], **kwargs)