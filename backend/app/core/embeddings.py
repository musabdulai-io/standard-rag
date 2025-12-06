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

    async def embed_batch(
        self, texts: List[str], batch_size: int = 50, max_chars: int = 20000
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        Processes in batches to avoid exceeding OpenAI's token limits.
        Individual texts are truncated to max_chars (~6000 tokens) if needed.
        OpenAI limit is 8192 tokens, but token density varies by content.
        """
        if not self.client:
            await self.initialize()

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        # Truncate texts that exceed token limit (8191 tokens ≈ 28000 chars)
        truncated_texts = []
        for text in texts:
            if len(text) > max_chars:
                truncated_texts.append(text[:max_chars])
                logs.warning(
                    f"Truncated text from {len(text)} to {max_chars} chars",
                    "embeddings",
                )
            else:
                truncated_texts.append(text)

        all_embeddings = []

        # Process in batches to avoid exceeding OpenAI API limits
        for i in range(0, len(truncated_texts), batch_size):
            batch = truncated_texts[i : i + batch_size]

            try:
                response = await self.client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "input": batch,
                        "dimensions": self.dimension,
                    },
                )
                response.raise_for_status()

                data = response.json()
                embeddings = [item["embedding"] for item in data["data"]]
                all_embeddings.extend(embeddings)

            except httpx.HTTPStatusError as e:
                # Log the actual error response from OpenAI
                try:
                    error_body = e.response.json()
                except Exception:
                    error_body = e.response.text
                logs.error(
                    "OpenAI API request failed",
                    "embeddings",
                    exception=e,
                    metadata={
                        "status_code": e.response.status_code,
                        "batch_start": i,
                        "batch_size": len(batch),
                        "error_body": str(error_body)[:500],
                        "max_text_len": max(len(t) for t in batch) if batch else 0,
                    },
                )
                raise
            except Exception as e:
                logs.error(
                    "Embedding request failed",
                    "embeddings",
                    exception=e,
                )
                raise

        logs.debug(
            f"Generated {len(all_embeddings)} embeddings",
            "embeddings",
        )

        return all_embeddings

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
