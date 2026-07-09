# backend/app/vectorstore/chroma.py

import chromadb
from typing import Any
import os

class ChromaVectorStore:
    """ChromaDB implementation of the Vector Store."""

    def __init__(self, collection_name: str = "documents"):
        # Ensure the persistence directory exists
        persist_dir = "./storage/chroma_db"
        os.makedirs(persist_dir, exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    async def add_documents(self, ids: list[str], texts: list[str], embeddings: list[list[float]], metadatas: list[dict]) -> None:
        if not ids:
            return
            
        # Chroma requires metadata values to be str, int, float, or bool
        clean_metadatas = []
        for meta in metadatas:
            clean_meta = {k: v for k, v in meta.items() if isinstance(v, (str, int, float, bool))}
            clean_metadatas.append(clean_meta)
            
        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=clean_metadatas
        )

    async def search(self, query_embedding: list[float], top_k: int = 5, filter: dict | None = None) -> list[dict[str, Any]]:
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
        }
        if filter:
            kwargs["where"] = filter

        results = self.collection.query(**kwargs)
        
        formatted = []
        if results and results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                formatted.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "id": results['ids'][0][i],
                    "distance": results['distances'][0][i] if results['distances'] else None
                })
        return formatted

    async def delete(self, ids: list[str]) -> None:
        if ids:
            self.collection.delete(ids=ids)