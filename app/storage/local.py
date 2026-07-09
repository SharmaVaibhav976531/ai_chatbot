# backend/app/storage/local.py

import os
import aiofiles
from app.storage.base import BaseStorage

class LocalStorage:
    """Local file system storage implementation."""

    def __init__(self, base_dir: str = "./storage/documents"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def save(self, file_content: bytes, destination: str) -> str:
        full_path = os.path.join(self.base_dir, destination)
        async with aiofiles.open(full_path, 'wb') as f:
            await f.write(file_content)
        return full_path

    async def delete(self, path: str) -> None:
        if os.path.exists(path):
            os.remove(path)