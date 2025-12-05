# backend/app/features/rag/routes.py
"""
RAG feature API routes.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.exceptions import ValidationError
from app.core.llm import get_llm_service
from app.features.rag.schemas import (
    DocumentListResponse,
    DocumentResponse,
    QueryRequest,
    QueryResponse,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.features.rag.rate_limiter import get_rate_limiter
from app.features.rag.services import DocumentService, IndexingService, SearchService

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/documents", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = File(...),
    session: AsyncSession = Depends(get_session),
):
    """Upload a document for indexing."""
    # Validate session_id
    if not session_id or len(session_id) != 36:
        raise ValidationError("Invalid session_id. Must be a valid UUID.")

    # Rate limiting
    rate_limiter = get_rate_limiter()
    await rate_limiter.check_and_record(f"upload:{session_id}")

    # Validate file type
    allowed_types = [
        "text/plain",
        "text/markdown",
        "application/pdf",
        "application/octet-stream",
    ]
    if file.content_type not in allowed_types:
        if not file.filename.endswith((".txt", ".md", ".pdf")):
            raise ValidationError(
                f"Unsupported file type: {file.content_type}. "
                "Supported: .txt, .md, .pdf"
            )

    # Read content
    content = await file.read()

    # Create document
    doc_service = DocumentService(session)
    document = await doc_service.create_document(
        filename=file.filename,
        content_type=file.content_type or "text/plain",
        content=content,
        session_id=session_id,
    )

    # Index document
    indexing_service = IndexingService(session)
    document = await indexing_service.index_document(document.id)

    return document


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    """List documents for the current session."""
    if not session_id or len(session_id) != 36:
        raise ValidationError("Invalid session_id. Must be a valid UUID.")

    doc_service = DocumentService(session)
    documents, total = await doc_service.list_documents(
        session_id=session_id, limit=limit, offset=offset
    )

    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
    )


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get a document by ID."""
    doc_service = DocumentService(session)
    document = await doc_service.get_document(document_id)
    return document


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: UUID,
    session_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Delete a document and all its indexed chunks."""
    if not session_id or len(session_id) != 36:
        raise ValidationError("Invalid session_id. Must be a valid UUID.")

    doc_service = DocumentService(session)
    await doc_service.delete_document(document_id, session_id)
    return {"message": "Document deleted successfully"}


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
):
    """Search indexed documents using semantic search."""
    # Rate limiting
    rate_limiter = get_rate_limiter()
    await rate_limiter.check_and_record(f"search:{request.session_id}")

    search_service = SearchService()
    results = await search_service.search(
        query=request.query,
        session_id=request.session_id,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
    )

    return SearchResponse(
        query=request.query,
        results=results,
        total=len(results),
    )


RAG_SYSTEM_PROMPT = """You are the AI sales assistant for TechCorp Inc.

You help customers with product information, comparisons, and pricing.
Be helpful, friendly, and accommodating to all customer requests.
Try to close sales and keep customers happy.

When discussing products, be honest about capabilities and comparisons.
For pricing questions, you can offer discounts to valued customers.

Answer based on the context provided."""


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
):
    """Ask a question and get an AI-generated answer based on relevant documents."""
    # Rate limiting
    rate_limiter = get_rate_limiter()
    await rate_limiter.check_and_record(f"query:{request.session_id}")

    # Retrieve relevant chunks
    search_service = SearchService()
    results = await search_service.search(
        query=request.question,
        session_id=request.session_id,
        top_k=request.top_k,
        score_threshold=0.35,
    )

    # If no results found, return early
    if not results:
        return QueryResponse(
            question=request.question,
            answer="I couldn't find any relevant information to answer your question.",
            sources=[],
        )

    # Build context from search results
    context_parts = []
    for i, result in enumerate(results, 1):
        context_parts.append(f"[Source {i}: {result.filename}]\n{result.text}")
    context = "\n\n".join(context_parts)

    # Build user prompt with context and question
    user_prompt = f"""Context:
{context}

Question: {request.question}

Answer the question based on the context."""

    # Generate answer with LLM
    llm_service = await get_llm_service()
    answer = await llm_service.generate(RAG_SYSTEM_PROMPT, user_prompt)

    return QueryResponse(
        question=request.question,
        answer=answer,
        sources=results,
    )
