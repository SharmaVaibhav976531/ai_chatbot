# backend/app/services/document.py

import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ForbiddenException
from app.repositories.document import DocumentRepository
from app.schemas.document import DocumentResponse

class DocumentService:
    """Service for handling document management business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.doc_repo = DocumentRepository(session)

    async def create_document(self, user_id: int, filename: str, file_type: str, file_size: int, storage_path: str) -> DocumentResponse:
        """Creates a new document record in the database."""
        doc = await self.doc_repo.create(user_id, filename, file_type, file_size, storage_path)
        return DocumentResponse.model_validate(doc)

    async def get_user_documents(self, user_id: int, skip: int, limit: int) -> list[DocumentResponse]:
        docs = await self.doc_repo.get_user_documents(user_id, skip, limit)
        return [DocumentResponse.model_validate(d) for d in docs]

    async def get_document(self, document_id: uuid.UUID, user_id: int) -> DocumentResponse:
        doc = await self.doc_repo.get(document_id)
        if not doc:
            raise NotFoundException("Document not found")
        if doc.user_id != user_id:
            raise ForbiddenException("Not authorized to access this document")
        return DocumentResponse.model_validate(doc)

    async def delete_document(self, document_id: uuid.UUID, user_id: int) -> bool:
        await self.get_document(document_id, user_id) # Validates existence and ownership
        # Note: In Phase 6 (RAG), we will also delete the file from storage and chunks from the Vector DB
        return await self.doc_repo.delete(document_id)