# backend/app/vectorstore/faiss.py (Refined for Deletion Support)

import faiss
import json
import os
import numpy as np
import asyncio
from typing import Any

class FAISSVectorStore:
    """FAISS implementation with local persistence and deletion support."""

    def __init__(self, dimension: int = 1536, storage_dir: str = "./storage/faiss"):
        self.dimension = dimension
        self.storage_dir = storage_dir
        self.index_path = os.path.join(storage_dir, "faiss.index")
        self.data_path = os.path.join(storage_dir, "faiss_data.json")

        os.makedirs(storage_dir, exist_ok=True)

        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            base_index = faiss.IndexFlatL2(dimension)
            self.index = faiss.IndexIDMap(base_index)

        if os.path.exists(self.data_path):
            with open(self.data_path, "r") as f:
                self.data_store: dict[str, dict] = json.load(f)
        else:
            self.data_store = {}

        self.next_int_id = max((v["int_id"] for v in self.data_store.values()), default=0) + 1

    def _save_state(self) -> None:
        faiss.write_index(self.index, self.index_path)
        with open(self.data_path, "w") as f:
            json.dump(self.data_store, f)

    async def add_documents(
        self, ids: list[str], texts: list[str], embeddings: list[list[float]], metadatas: list[dict]
    ) -> None:
        if not ids: return

        int_ids = []
        valid_vectors = []
        
        for i, str_id in enumerate(ids):
            if str_id not in self.data_store:
                int_id = self.next_int_id
                self.next_int_id += 1
            else:
                int_id = self.data_store[str_id]["int_id"]
                
            self.data_store[str_id] = {
                "int_id": int_id,
                "content": texts[i],
                "metadata": metadatas[i],
                "vector": embeddings[i] # Store vector locally for rebuilds/deletions
            }
            int_ids.append(int_id)
            valid_vectors.append(embeddings[i])

        vectors = np.array(valid_vectors, dtype=np.float32)
        faiss_ids = np.array(int_ids, dtype=np.int64)

        await asyncio.to_thread(self.index.add_with_ids, vectors, faiss_ids)
        await asyncio.to_thread(self._save_state)

    async def search(
        self, query_embedding: list[float], top_k: int = 5, filter: dict | None = None
    ) -> list[dict[str, Any]]:
        if self.index.ntotal == 0: return []

        fetch_k = min(top_k * 3 if filter else top_k, self.index.ntotal)
        query_vec = np.array([query_embedding], dtype=np.float32)
        
        distances, int_ids = await asyncio.to_thread(self.index.search, query_vec, fetch_k)

        results = []
        for dist, int_id in zip(distances[0], int_ids[0]):
            if int_id == -1: continue
                
            str_id = next((k for k, v in self.data_store.items() if v["int_id"] == int_id), None)
            if not str_id: continue

            data = self.data_store[str_id]
            if filter and not all(data["metadata"].get(k) == v for k, v in filter.items()):
                continue

            results.append({
                "id": str_id,
                "content": data["content"],
                "metadata": data["metadata"],
                "distance": float(dist)
            })
            if len(results) >= top_k: break

        return results

    async def delete(self, ids: list[str]) -> None:
        if not ids: return

        ids_to_remove = [str_id for str_id in ids if str_id in self.data_store]
        if not ids_to_remove: return

        int_ids_to_remove = [self.data_store[str_id]["int_id"] for str_id in ids_to_remove]
        
        for str_id in ids_to_remove:
            del self.data_store[str_id]

        # Rebuild index without removed IDs
        await self._rebuild_index()
        await asyncio.to_thread(self._save_state)

    async def _rebuild_index(self) -> None:
        """Rebuilds the FAISS index from the local data store."""
        base_index = faiss.IndexFlatL2(self.dimension)
        self.index = faiss.IndexIDMap(base_index)
        
        if self.data_store:
            vectors = np.array([d["vector"] for d in self.data_store.values()], dtype=np.float32)
            faiss_ids = np.array([d["int_id"] for d in self.data_store.values()], dtype=np.int64)
            self.index.add_with_ids(vectors, faiss_ids)

            