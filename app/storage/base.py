# backend/app/storage/base.py

from typing import Protocol

class BaseStorage(Protocol):
    """Protocol for file storage operations."""

    async def save(self, file_content: bytes, destination: str) -> str:
        """Saves file content and returns the storage path/URL."""
        ...

    async def delete(self, path: str) -> None:
        """Deletes a file from storage."""
        ...