# backend/app/tools/web_search.py

import json
import asyncio
from duckduckgo_search import DDGS
from app.tools.base import BaseTool

class WebSearchTool:
    """Searches the web using DuckDuckGo."""
    name = "web_search"
    description = "Useful for searching the web for current events, news, or general knowledge. Input should be a search query."

    async def run(self, input_data: str) -> str:
        def _search():
            with DDGS() as ddgs:
                results = list(ddgs.text(input_data, max_results=5))
                return results

        try:
            results = await asyncio.to_thread(_search)
            if not results:
                return "No search results found."
            
            formatted = []
            for r in results:
                formatted.append(f"Title: {r.get('title', 'N/A')}\nSnippet: {r.get('body', 'N/A')}\nURL: {r.get('href', 'N/A')}")
            return "\n\n---\n\n".join(formatted)
        except Exception as e:
            return f"Search error: {str(e)}"