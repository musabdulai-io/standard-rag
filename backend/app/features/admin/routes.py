# backend/app/features/admin/routes.py
"""
Admin API routes for test document management.

Test documents (is_sample=True) are visible to ALL sessions,
making them ideal for scanner quality testing.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.exceptions import NotFoundError, ValidationError
from app.core.observability import logs
from app.core.pinecone import get_pinecone_store
from app.core.storage import get_storage
from app.features.rag.models import Document
from app.features.rag.schemas import DocumentResponse, DocumentListResponse
from app.features.rag.services import DocumentService, IndexingService

router = APIRouter(prefix="/admin", tags=["Admin"])

# Special session ID for sample/test documents
SAMPLE_SESSION_ID = "00000000-0000-0000-0000-000000000000"

# Allowed content types for admin uploads (more permissive)
ALLOWED_CONTENT_TYPES = [
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # xlsx
    "application/vnd.ms-excel",  # xls
    "application/json",
]


class AdminDocumentResponse(BaseModel):
    """Response for admin document operations."""
    id: UUID
    filename: str
    content_type: str
    file_size: int
    status: str
    category: Optional[str] = None
    message: str


@router.post("/documents", response_model=AdminDocumentResponse)
async def upload_test_document(
    file: UploadFile = File(...),
    category: str = Form(default="general"),
    session: AsyncSession = Depends(get_session),
):
    """
    Upload a test document visible to ALL sessions.

    Test documents are marked with is_sample=True and stored with a special
    session_id, making them queryable by any session (including the scanner).

    Categories:
    - tables: PDF/Excel with complex tables (SEC 10-K, pricing matrices)
    - ocr: Scanned documents for OCR testing
    - haystack: Large documents for needle-in-haystack tests
    - vulnerable: Documents designed to cause RAG failures
    - fixtures: Documents with known answers for verification
    - general: Default category
    """
    # Validate file type (be permissive for admin)
    content_type = file.content_type or "application/octet-stream"

    # Read file content
    content = await file.read()
    if len(content) == 0:
        raise ValidationError("Empty file uploaded")

    # Size limit: 50MB for admin uploads (larger than user uploads)
    max_size = 50 * 1024 * 1024
    if len(content) > max_size:
        raise ValidationError(f"File too large. Maximum size is {max_size // (1024*1024)}MB")

    try:
        # Create document with sample flag
        doc_service = DocumentService(session)
        document = await doc_service.create_document(
            filename=file.filename or "unknown",
            content_type=content_type,
            content=content,
            session_id=SAMPLE_SESSION_ID,
            is_sample=True,
        )

        # Index the document
        indexing_service = IndexingService(session)
        await indexing_service.index_document(document.id)

        logs.info(
            f"Test document uploaded: {document.id}",
            "admin",
            metadata={
                "filename": file.filename,
                "category": category,
                "size": len(content),
            },
        )

        return AdminDocumentResponse(
            id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            file_size=document.file_size,
            status=document.status,
            category=category,
            message=f"Test document uploaded and indexed. Visible to all sessions.",
        )

    except Exception as e:
        logs.error(f"Failed to upload test document: {e}", "admin")
        raise


@router.get("/documents", response_model=DocumentListResponse)
async def list_test_documents(
    session: AsyncSession = Depends(get_session),
):
    """
    List all test/sample documents.

    Returns documents where is_sample=True, which are visible to all sessions.
    """
    result = await session.execute(
        select(Document)
        .where(Document.is_sample == True)
        .order_by(Document.created_at.desc())
    )
    documents = result.scalars().all()

    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(doc) for doc in documents],
        total=len(documents),
    )


@router.delete("/documents/{document_id}")
async def delete_test_document(
    document_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a test document.

    Only documents with is_sample=True can be deleted via this endpoint.
    """
    # Get document
    result = await session.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise NotFoundError(f"Document not found: {document_id}")

    if not document.is_sample:
        raise ValidationError("Only test documents (is_sample=True) can be deleted via admin API")

    # Delete from Pinecone
    pinecone = await get_pinecone_store()
    await pinecone.delete_document(document_id)

    # Delete from storage
    storage = get_storage()
    await storage.delete(document.storage_path)

    # Delete from database
    await session.delete(document)
    await session.commit()

    logs.info(f"Test document deleted: {document_id}", "admin")

    return {"message": f"Test document {document_id} deleted", "id": str(document_id)}


@router.delete("/documents")
async def delete_all_test_documents(
    session: AsyncSession = Depends(get_session),
):
    """
    Delete ALL test documents.

    Use with caution - this removes all sample documents from the system.
    """
    # Get all sample documents
    result = await session.execute(
        select(Document).where(Document.is_sample == True)
    )
    documents = result.scalars().all()

    if not documents:
        return {"message": "No test documents to delete", "deleted_count": 0}

    deleted_count = 0
    pinecone = await get_pinecone_store()
    storage = get_storage()

    for document in documents:
        try:
            # Delete from Pinecone
            await pinecone.delete_document(document.id)

            # Delete from storage
            await storage.delete(document.storage_path)

            # Delete from database
            await session.delete(document)
            deleted_count += 1

        except Exception as e:
            logs.error(f"Failed to delete document {document.id}: {e}", "admin")

    await session.commit()

    logs.info(f"Deleted {deleted_count} test documents", "admin")

    return {"message": f"Deleted {deleted_count} test documents", "deleted_count": deleted_count}
