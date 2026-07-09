# backend/app/tools/document_search.py

from app.tools.base import BaseTool
from app.vectorstore.factory import VectorStoreFactory
from app.embeddings.factory import EmbeddingsFactory
from app.core.config import settings

class DocumentSearchTool:
    """Searches the internal vector database for relevant document chunks."""
    name = "document_search"
    description = "Useful for searching internal uploaded documents. Input should be a semantic query."

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.vectorstore = VectorStoreFactory.get_vector_store()
        self.embeddings = EmbeddingsFactory.get_embeddings(settings.EMBEDDINGS_PROVIDER, settings.EMBEDDINGS_MODEL)

    async def run(self, input_data: str) -> str:
        try:
            query_embedding = await self.embeddings.embed_query(input_data)
            results = await self.vectorstore.search(
                query_embedding, 
                top_k=3, 
                filter={"user_id": self.user_id}
            )
            
            if not results:
                return "No relevant documents found."
                
            formatted = []
            for r in results:
                formatted.append(f"[Doc: {r['metadata'].get('filename', 'Unknown')}]\n{r['content']}")
            return "\n\n---\n\n".join(formatted)
        except Exception as e:
            return f"Document search error: {str(e)}"