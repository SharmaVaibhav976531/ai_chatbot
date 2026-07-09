# backend/app/repositories/document.py

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document, DocumentStatus

class DocumentRepository:
    """Repository for Document database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, document_id: uuid.UUID) -> Document | None:
        result = await self.session.execute(select(Document).where(Document.id == document_id))
        return result.scalar_one_or_none()

    async def get_user_documents(self, user_id: int, skip: int = 0, limit: int = 50) -> list[Document]:
        result = await self.session.execute(
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, user_id: int, filename: str, file_type: str, file_size: int, storage_path: str) -> Document:
        db_obj = Document(
            user_id=user_id, 
            filename=filename, 
            file_type=file_type, 
            file_size=file_size, 
            storage_path=storage_path,
            status=DocumentStatus.PENDING
        )
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update_status(self, document_id: uuid.UUID, status: DocumentStatus) -> Document | None:
        db_obj = await self.get(document_id)
        if not db_obj:
            return None
        db_obj.status = status
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, document_id: uuid.UUID) -> bool:
        db_obj = await self.get(document_id)
        if not db_obj:
            return False
        await self.session.delete(db_obj)
        await self.session.commit()
        return True