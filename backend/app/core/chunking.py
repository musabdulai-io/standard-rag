# backend/app/core/chunking.py
"""
Document chunking utilities for RAG.
Implements semantic chunking with 1-2KB target size.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List
from uuid import UUID, NAMESPACE_DNS, uuid5

from app.core.config import settings


@dataclass
class DocumentChunk:
    """Represents a chunk of a document."""

    id: str
    document_id: UUID
    text: str
    char_start: int
    char_end: int
    chunk_index: int
    metadata: Dict[str, Any]


class SemanticChunker:
    """
    Chunks documents at semantic boundaries (paragraphs, sentences).
    Target chunk size: 1-2KB (approximately 150-300 words).
    """

    def __init__(
        self,
        min_chunk_size: int = None,
        max_chunk_size: int = None,
        overlap_size: int = None,
    ):
        """Initialize chunker with size parameters from settings."""
        self.min_chunk_size = min_chunk_size or settings.CHUNK_MIN_SIZE
        self.max_chunk_size = max_chunk_size or settings.CHUNK_MAX_SIZE
        self.overlap_size = overlap_size or settings.CHUNK_OVERLAP

    def chunk_text(
        self,
        text: str,
        document_id: UUID,
        metadata: Dict[str, Any] | None = None,
    ) -> List[DocumentChunk]:
        """
        Split text into semantic chunks.

        Args:
            text: Full document text
            document_id: UUID of the parent document
            metadata: Additional metadata to attach to each chunk

        Returns:
            List of DocumentChunk objects
        """
        if not text or not text.strip():
            return []

        metadata = metadata or {}
        paragraphs = self._split_into_paragraphs(text)

        chunks: List[DocumentChunk] = []
        current_chunk = ""
        current_start = 0
        chunk_index = 0

        for para in paragraphs:
            if len(para.encode("utf-8")) > self.max_chunk_size:
                if current_chunk:
                    chunks.append(
                        self._create_chunk(
                            text=current_chunk.strip(),
                            document_id=document_id,
                            char_start=current_start,
                            char_end=current_start + len(current_chunk),
                            chunk_index=chunk_index,
                            metadata=metadata,
                        )
                    )
                    chunk_index += 1

                sentence_chunks = self._chunk_sentences(
                    para, document_id, chunk_index, metadata
                )
                chunks.extend(sentence_chunks)
                chunk_index += len(sentence_chunks)

                current_chunk = ""
                current_start = text.find(para) + len(para)

            else:
                test_chunk = current_chunk + "\n\n" + para if current_chunk else para
                test_size = len(test_chunk.encode("utf-8"))

                if test_size > self.max_chunk_size and current_chunk:
                    chunks.append(
                        self._create_chunk(
                            text=current_chunk.strip(),
                            document_id=document_id,
                            char_start=current_start,
                            char_end=current_start + len(current_chunk),
                            chunk_index=chunk_index,
                            metadata=metadata,
                        )
                    )
                    chunk_index += 1

                    current_chunk = para
                    current_start = text.find(para)

                else:
                    if current_chunk:
                        current_chunk += "\n\n" + para
                    else:
                        current_chunk = para
                        current_start = text.find(para)

        if current_chunk and len(current_chunk.strip()) > 50:
            chunks.append(
                self._create_chunk(
                    text=current_chunk.strip(),
                    document_id=document_id,
                    char_start=current_start,
                    char_end=current_start + len(current_chunk),
                    chunk_index=chunk_index,
                    metadata=metadata,
                )
            )

        return chunks

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        paragraphs = re.split(r"\n\s*\n+", text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _chunk_sentences(
        self,
        text: str,
        document_id: UUID,
        start_index: int,
        metadata: Dict[str, Any],
    ) -> List[DocumentChunk]:
        """Split large text by sentences when paragraph is too big."""
        sentences = re.split(r"(?<=[.!?])\s+", text)

        chunks: List[DocumentChunk] = []
        current_chunk = ""
        chunk_index = start_index

        for sentence in sentences:
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            test_size = len(test_chunk.encode("utf-8"))

            if test_size > self.max_chunk_size and current_chunk:
                chunks.append(
                    self._create_chunk(
                        text=current_chunk.strip(),
                        document_id=document_id,
                        char_start=0,
                        char_end=len(current_chunk),
                        chunk_index=chunk_index,
                        metadata=metadata,
                    )
                )
                chunk_index += 1
                current_chunk = sentence
            else:
                current_chunk = test_chunk

        if current_chunk:
            chunks.append(
                self._create_chunk(
                    text=current_chunk.strip(),
                    document_id=document_id,
                    char_start=0,
                    char_end=len(current_chunk),
                    chunk_index=chunk_index,
                    metadata=metadata,
                )
            )

        return chunks

    def _create_chunk(
        self,
        text: str,
        document_id: UUID,
        char_start: int,
        char_end: int,
        chunk_index: int,
        metadata: Dict[str, Any],
    ) -> DocumentChunk:
        """Create a DocumentChunk object."""
        # Generate deterministic UUID from document_id and chunk_index
        # Qdrant requires UUIDs or integers for point IDs
        chunk_id_str = f"{document_id}_{chunk_index}"
        chunk_id = str(uuid5(NAMESPACE_DNS, chunk_id_str))

        return DocumentChunk(
            id=chunk_id,
            document_id=document_id,
            text=text,
            char_start=char_start,
            char_end=char_end,
            chunk_index=chunk_index,
            metadata=metadata,
        )


def get_chunker() -> SemanticChunker:
    """Get default semantic chunker instance."""
    return SemanticChunker()
