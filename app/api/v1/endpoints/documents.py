# backend/app/api/v1/endpoints/documents.py

import os
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, Query, status, APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_session
from app.api.deps import CurrentUser
from app.schemas.document import DocumentResponse
from app.services.document import DocumentService
from app.services.rag_pipeline import process_document_task
from app.core.exceptions import BadRequestException

router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt", "csv", "md", "markdown"}
MAX_FILE_SIZE_MB = 50

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    file: UploadFile = File(...)
) -> DocumentResponse:
    """Uploads a document and triggers background processing for RAG."""
    if not file.filename:
        raise BadRequestException("Filename is required")
        
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise BadRequestException(f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}")

    # Read file content
    content = await file.read()
    file_size = len(content)
    
    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise BadRequestException(f"File size exceeds maximum limit of {MAX_FILE_SIZE_MB}MB")

    # Save to local storage (In production, this would be S3/GCS)
    storage_dir = "./storage/documents"
    os.makedirs(storage_dir, exist_ok=True)
    file_id = uuid.uuid4()
    storage_filename = f"{file_id}.{ext}"
    storage_path = os.path.join(storage_dir, storage_filename)
    
    with open(storage_path, "wb") as f:
        f.write(content)

    # Create DB record
    doc_service = DocumentService(session)
    doc = await doc_service.create_document(
        user_id=current_user.id,
        filename=file.filename,
        file_type=ext,
        file_size=file_size,
        storage_path=storage_path
    )

    # Trigger background RAG processing
    background_tasks.add_task(process_document_task, doc.id, content)

    return DocumentResponse.model_validate(doc)

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