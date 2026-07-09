# backend/app/services/rag_pipeline.py

import uuid
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.repositories.document import DocumentRepository
from app.services.document_extraction import DocumentExtractor
from app.services.document_chunking import DocumentChunker
from app.embeddings.factory import EmbeddingsFactory
from app.vectorstore.chroma import ChromaVectorStore
from app.core.config import settings

logger = structlog.get_logger()

class RAGPipeline:
    """Orchestrates the RAG document processing pipeline."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.doc_repo = DocumentRepository(session)
        self.extractor = DocumentExtractor()
        self.chunker = DocumentChunker()
        self.embeddings = EmbeddingsFactory.get_embeddings(
            settings.EMBEDDINGS_PROVIDER, 
            settings.EMBEDDINGS_MODEL
        )
        self.vectorstore = ChromaVectorStore()

    async def process_document(self, document_id: uuid.UUID, file_content: bytes) -> None:
        """Executes the full RAG pipeline for a single document."""
        doc = await self.doc_repo.get(document_id)
        if not doc:
            logger.error("document_not_found_for_processing", document_id=document_id)
            return

        try:
            await self.doc_repo.update_status(document_id, DocumentStatus.PROCESSING)
            
            # 1. Extract text
            text = await self.extractor.extract(doc.file_type, file_content)
            if not text.strip():
                raise ValueError("Extracted text is empty or unreadable")

            # 2. Chunk text
            base_metadata = {"document_id": str(document_id), "filename": doc.filename, "user_id": doc.user_id}
            chunks_data = self.chunker.chunk_text(text, base_metadata)
            
            if not chunks_data:
                raise ValueError("No chunks generated from document")

            # 3. Generate embeddings
            texts = [c["content"] for c in chunks_data]
            embeddings = await self.embeddings.embed_documents(texts)
            
            # 4. Save chunks to relational DB
            db_chunks = []
            vector_ids = []
            for i, chunk_data in enumerate(chunks_data):
                chunk_id = uuid.uuid4()
                vector_id = f"{document_id}_{i}"
                
                db_chunk = DocumentChunk(
                    id=chunk_id,
                    document_id=document_id,
                    chunk_index=i,
                    content=chunk_data["content"],
                    metadata_=chunk_data["metadata"],
                    vector_id=vector_id
                )
                db_chunks.append(db_chunk)
                vector_ids.append(vector_id)

            self.session.add_all(db_chunks)
            await self.session.commit()

            # 5. Add to Vector Store
            metadatas = [c["metadata"] for c in chunks_data]
            await self.vectorstore.add_documents(
                ids=vector_ids, 
                texts=texts, 
                embeddings=embeddings, 
                metadatas=metadatas
            )

            await self.doc_repo.update_status(document_id, DocumentStatus.READY)
            logger.info("document_processed_successfully", document_id=document_id, chunks=len(chunks_data))

        except Exception as e:
            logger.exception("document_processing_failed", document_id=document_id, error=str(e))
            await self.doc_repo.update_status(document_id, DocumentStatus.FAILED)


async def process_document_task(document_id: uuid.UUID, file_content: bytes) -> None:
    """
    Background task wrapper for the RAG pipeline.
    Creates its own database session to avoid issues with the main request session closing.
    """
    from app.database.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        pipeline = RAGPipeline(session)
        await pipeline.process_document(document_id, file_content)