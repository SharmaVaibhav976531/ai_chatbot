# backend/app/services/document_extraction.py

import io
import asyncio
from pypdf import PdfReader
from docx import Document as DocxDocument
from app.core.exceptions import BadRequestException

class DocumentExtractor:
    """Extracts text content from various document formats."""

    @staticmethod
    async def extract(file_type: str, file_content: bytes) -> str:
        """Routes the extraction to the appropriate handler based on file type."""
        file_type = file_type.lower()
        
        if file_type == "pdf":
            return await asyncio.to_thread(DocumentExtractor._extract_pdf, file_content)
        elif file_type == "docx":
            return await asyncio.to_thread(DocumentExtractor._extract_docx, file_content)
        elif file_type in ["txt", "md", "markdown", "csv"]:
            return file_content.decode("utf-8", errors="ignore")
        else:
            raise BadRequestException(f"Unsupported file type for extraction: {file_type}")

    @staticmethod
    def _extract_pdf(content: bytes) -> str:
        reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()

    @staticmethod
    def _extract_docx(content: bytes) -> str:
        doc = DocxDocument(io.BytesIO(content))
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        return text.strip()