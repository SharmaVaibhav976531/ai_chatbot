# backend/app/services/document_chunking.py

from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentChunker:
    """Splits document text into smaller chunks for embedding and retrieval."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def chunk_text(self, text: str, base_metadata: dict) -> list[dict]:
        """
        Splits text into chunks and attaches metadata to each chunk.
        
        Args:
            text: The raw text to be chunked.
            base_metadata: Base metadata to attach to every chunk (e.g., document_id, filename).
            
        Returns:
            A list of dictionaries containing 'content' and 'metadata'.
        """
        chunks = self.splitter.split_text(text)
        return [
            {
                "content": chunk.strip(),
                "metadata": {**base_metadata, "chunk_index": i, "chunk_length": len(chunk)}
            }
            for i, chunk in enumerate(chunks) if chunk.strip()
        ]