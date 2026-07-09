# backend/app/storage/factory.py

from app.storage.base import BaseStorage
from app.storage.local import LocalStorage
from app.storage.s3 import S3Storage
from app.core.config import settings

class StorageFactory:
    """Factory for creating Storage instances."""

    @classmethod
    def get_storage(cls) -> BaseStorage:
        provider = settings.STORAGE_PROVIDER.lower()
        if provider == "s3":
            return S3Storage()
        return LocalStorage()