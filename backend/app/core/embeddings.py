# backend/app/core/embeddings.py
"""
OpenAI embedding service for RAG.
"""

from __future__ import annotations

from typing import List, Optional

import httpx

from app.core.config import settings
from app.core.observability import logs


class EmbeddingService:
    """OpenAI embedding service using text-embedding-3-small."""

    def __init__(self) -> None:
        """Initialize embedding service."""
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_EMBEDDING_MODEL
        self.dimension = settings.OPENAI_EMBEDDING_DIMENSION
        self.client: Optional[httpx.AsyncClient] = None

    async def initialize(self) -> None:
        """Initialize the HTTP client."""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=30.0)
            logs.info(
                "Embedding service initialized",
                "embeddings",
                metadata={"model": self.model},
            )

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        result = await self.embed_batch([text])
        return result[0]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        if not self.client:
            await self.initialize()

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        try:
            response = await self.client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "input": texts,
                    "dimensions": self.dimension,
                },
            )
            response.raise_for_status()

            data = response.json()
            embeddings = [item["embedding"] for item in data["data"]]

            logs.debug(
                f"Generated {len(embeddings)} embeddings",
                "embeddings",
            )

            return embeddings

        except httpx.HTTPStatusError as e:
            logs.error(
                "OpenAI API request failed",
                "embeddings",
                exception=e,
                metadata={"status_code": e.response.status_code},
            )
            raise
        except Exception as e:
            logs.error(
                "Embedding request failed",
                "embeddings",
                exception=e,
            )
            raise

    async def close(self) -> None:
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None


# Global instance
_embedding_service: Optional[EmbeddingService] = None


async def get_embedding_service() -> EmbeddingService:
    """Get or create the global embedding service instance."""
    global _embedding_service

    if _embedding_service is None:
        _embedding_service = EmbeddingService()
        await _embedding_service.initialize()

    return _embedding_service
