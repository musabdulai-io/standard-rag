# backend/app/features/rag/schemas.py
"""
RAG feature API schemas.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# Document schemas
class DocumentCreate(BaseModel):
    """Schema for document upload metadata."""

    filename: str
    content_type: str


class DocumentResponse(BaseModel):
    """Schema for document response."""

    id: UUID
    filename: str
    content_type: str
    file_size: int
    status: str
    chunk_count: int
    error_message: Optional[str] = None
    is_sample: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for list of documents."""

    documents: List[DocumentResponse]
    total: int


# Search schemas
class SearchRequest(BaseModel):
    """Schema for search request."""

    query: str = Field(..., min_length=1, max_length=1000)
    session_id: str = Field(..., min_length=36, max_length=36)
    top_k: int = Field(default=10, ge=1, le=50)
    score_threshold: float = Field(default=0.35, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    """Schema for a single search result."""

    chunk_id: str
    document_id: UUID
    filename: str
    text: str
    score: float
    chunk_index: int


class SearchResponse(BaseModel):
    """Schema for search response."""

    query: str
    results: List[SearchResult]
    total: int


# Chat/Query schemas
class QueryRequest(BaseModel):
    """Schema for RAG query request."""

    question: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(..., min_length=36, max_length=36)
    top_k: int = Field(default=5, ge=1, le=20)


class QueryResponse(BaseModel):
    """Schema for RAG query response."""

    question: str
    answer: str
    sources: List[SearchResult]
