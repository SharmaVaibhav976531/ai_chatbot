# backend/app/api/v1/endpoints/documents.py

import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_session
from app.api.deps import CurrentUser
from app.schemas.document import DocumentResponse
from app.services.document import DocumentService

router = APIRouter()

@router.get("/", response_model=list[DocumentResponse], status_code=status.HTTP_200_OK)
async def list_documents(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
) -> list[DocumentResponse]:
    """Retrieves a list of documents for the current user."""
    doc_service = DocumentService(session)
    return await doc_service.get_user_documents(current_user.id, skip, limit)

@router.get("/{document_id}", response_model=DocumentResponse, status_code=status.HTTP_200_OK)
async def get_document(
    document_id: uuid.UUID,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> DocumentResponse:
    """Retrieves a specific document by ID."""
    doc_service = DocumentService(session)
    return await doc_service.get_document(document_id, current_user.id)

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> None:
    """Deletes a document and its associated chunks."""
    doc_service = DocumentService(session)
    await doc_service.delete_document(document_id, current_user.id)