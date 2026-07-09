# backend/app/llms/gemini.py

import asyncio
import google.generativeai as genai
from typing import AsyncGenerator, Any
from app.core.config import settings

class GeminiLLM:
    """Implementation for Google Gemini API."""

    def __init__(self, model: str = "gemini-pro"):
        self.model = model
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.client = genai.GenerativeModel(self.model)

    def _format_messages(self, messages: list[dict[str, Any]]) -> tuple[str | None, list[dict]]:
        """
        Gemini uses 'model' instead of 'assistant' for roles, and expects 
        content in a 'parts' array. System instructions are handled separately.
        """
        system_msg = None
        formatted = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                role = "model" if msg["role"] == "assistant" else msg["role"]
                formatted.append({"role": role, "parts": [msg["content"]]})
        return system_msg, formatted

    async def complete(self, messages: list[dict[str, Any]]) -> str:
        system, fmt_msgs = self._format_messages(messages)
        model = genai.GenerativeModel(self.model, system_instruction=system) if system else self.client
        
        def _sync_call() -> str:
            if fmt_msgs:
                history = fmt_msgs[:-1]
                prompt = fmt_msgs[-1]["parts"][0] if fmt_msgs else ""
                chat = model.start_chat(history=history)
                response = chat.send_message(prompt)
            else:
                response = model.generate_content("")
            return response.text

        # Wrap synchronous SDK call in a thread to avoid blocking the event loop
        return await asyncio.to_thread(_sync_call)

    async def stream(self, messages: list[dict[str, Any]]) -> AsyncGenerator[str, None]:
        system, fmt_msgs = self._format_messages(messages)
        model = genai.GenerativeModel(self.model, system_instruction=system) if system else self.client
        
        def _sync_stream():
            if fmt_msgs:
                history = fmt_msgs[:-1]
                prompt = fmt_msgs[-1]["parts"][0] if fmt_msgs else ""
                chat = model.start_chat(history=history)
                response = chat.send_message(prompt, stream=True)
            else:
                response = model.generate_content("", stream=True)
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text

        # Bridge the synchronous generator to an asynchronous one using an executor
        loop = asyncio.get_running_loop()
        sync_iter = iter(_sync_stream())
        
        while True:
            try:
                # Run the blocking next() call in a thread pool
                chunk = await loop.run_in_executor(None, next, sync_iter, None)
                if chunk is None:
                    break
                yield chunk
            except StopIteration:
                break