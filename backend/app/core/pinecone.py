# backend/app/core/pinecone.py
"""
Pinecone vector database client for RAG retrieval.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from pinecone import Pinecone, ServerlessSpec

from app.core.config import settings
from app.core.observability import logs


class PineconeVectorStore:
    """Pinecone client for managing vector search."""

    def __init__(self) -> None:
        """Initialize Pinecone client with configuration from settings."""
        self.client: Optional[Pinecone] = None
        self.index = None
        self.index_name = settings.PINECONE_INDEX
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize connection to Pinecone and create index if needed."""
        if self._initialized:
            return

        try:
            self.client = Pinecone(api_key=settings.PINECONE_API_KEY)

            # Check if index exists, create if not
            existing_indexes = [idx.name for idx in self.client.list_indexes()]

            if self.index_name not in existing_indexes:
                self.client.create_index(
                    name=self.index_name,
                    dimension=settings.OPENAI_EMBEDDING_DIMENSION,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud=settings.PINECONE_CLOUD,
                        region=settings.PINECONE_REGION,
                    ),
                )
                logs.info(f"Created Pinecone index: {self.index_name}", "pinecone")

            self.index = self.client.Index(self.index_name)
            self._initialized = True

            logs.info(
                "Pinecone client initialized",
                "pinecone",
                metadata={"index": self.index_name},
            )

        except Exception as e:
            logs.error("Failed to initialize Pinecone client", "pinecone", exception=e)
            raise

    async def index_chunk(
        self,
        chunk_id: str,
        document_id: UUID,
        embedding: List[float],
        metadata: Dict[str, Any],
    ) -> None:
        """Index a document chunk in the index."""
        if not self.index:
            raise RuntimeError("Pinecone client not initialized")

        vector = {
            "id": chunk_id,
            "values": embedding,
            "metadata": {
                "document_id": str(document_id),
                "chunk_id": chunk_id,
                **metadata,
            },
        }

        self.index.upsert(vectors=[vector])

    async def index_chunks_batch(
        self,
        chunks: List[Dict[str, Any]],
    ) -> None:
        """Index multiple chunks in a batch."""
        if not self.index:
            raise RuntimeError("Pinecone client not initialized")

        vectors = [
            {
                "id": chunk["chunk_id"],
                "values": chunk["embedding"],
                "metadata": {
                    "document_id": str(chunk["document_id"]),
                    "chunk_id": chunk["chunk_id"],
                    # Truncate text to 1000 chars to fit Pinecone metadata limits
                    "text": chunk.get("metadata", {}).get("text", "")[:1000],
                    "filename": chunk.get("metadata", {}).get("filename", ""),
                    "chunk_index": chunk.get("metadata", {}).get("chunk_index", 0),
                    "session_id": chunk.get("metadata", {}).get("session_id", ""),
                },
            }
            for chunk in chunks
        ]

        # Pinecone upsert in batches of 100
        for i in range(0, len(vectors), 100):
            batch = vectors[i : i + 100]
            self.index.upsert(vectors=batch)

        logs.info(f"Indexed {len(vectors)} chunks", "pinecone")

    async def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: float = 0.5,
        filter_conditions: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar chunks.

        Returns:
            List of (chunk_id, score, metadata) tuples
        """
        if not self.index:
            raise RuntimeError("Pinecone client not initialized")

        results = self.index.query(
            vector=query_embedding,
            top_k=limit,
            include_metadata=True,
        )

        # Filter by score threshold client-side
        return [
            (
                match.id,
                match.score,
                match.metadata or {},
            )
            for match in results.matches
            if match.score >= score_threshold
        ]

    async def delete_document(self, document_id: UUID) -> None:
        """Delete all chunks for a document."""
        if not self.index:
            raise RuntimeError("Pinecone client not initialized")

        # Pinecone delete by metadata filter
        self.index.delete(filter={"document_id": {"$eq": str(document_id)}})

        logs.info(f"Deleted document {document_id} from Pinecone", "pinecone")

    async def health_check(self) -> bool:
        """Check if Pinecone is healthy."""
        if not self.index:
            return False

        try:
            self.index.describe_index_stats()
            return True
        except Exception as e:
            logs.error("Pinecone health check failed", "pinecone", exception=e)
            return False

    async def close(self) -> None:
        """Close the Pinecone client connection."""
        # Pinecone client doesn't need explicit closing
        self._initialized = False


# Global instance
_pinecone_store: Optional[PineconeVectorStore] = None


async def get_pinecone_store() -> PineconeVectorStore:
    """Get or create the global Pinecone store instance."""
    global _pinecone_store

    if _pinecone_store is None:
        _pinecone_store = PineconeVectorStore()
        await _pinecone_store.initialize()

    return _pinecone_store
