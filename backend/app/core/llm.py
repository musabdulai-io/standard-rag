# backend/app/core/llm.py
"""
OpenAI LLM service for RAG generation.
"""

from __future__ import annotations

from typing import Optional

import httpx

from app.core.config import settings
from app.core.observability import logs


class LLMService:
    """OpenAI chat completions service using gpt-4o-mini."""

    def __init__(self) -> None:
        """Initialize LLM service."""
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_CHAT_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
        self.client: Optional[httpx.AsyncClient] = None

    async def initialize(self) -> None:
        """Initialize the HTTP client."""
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=60.0)
            logs.info(
                "LLM service initialized",
                "llm",
                metadata={"model": self.model},
            )

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate a response using OpenAI Chat Completions.

        Args:
            system_prompt: System instructions for the model
            user_prompt: User message/question with context

        Returns:
            Generated response text
        """
        if not self.client:
            await self.initialize()

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")

        try:
            response = await self.client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                },
            )
            response.raise_for_status()

            data = response.json()
            answer = data["choices"][0]["message"]["content"]

            logs.debug(
                "LLM generation completed",
                "llm",
                metadata={
                    "model": self.model,
                    "prompt_tokens": data.get("usage", {}).get("prompt_tokens"),
                    "completion_tokens": data.get("usage", {}).get("completion_tokens"),
                },
            )

            return answer

        except httpx.HTTPStatusError as e:
            logs.error(
                "OpenAI API request failed",
                "llm",
                exception=e,
                metadata={"status_code": e.response.status_code},
            )
            raise
        except Exception as e:
            logs.error(
                "LLM generation failed",
                "llm",
                exception=e,
            )
            raise

    async def close(self) -> None:
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None


# Global instance
_llm_service: Optional[LLMService] = None


async def get_llm_service() -> LLMService:
    """Get or create the global LLM service instance."""
    global _llm_service

    if _llm_service is None:
        _llm_service = LLMService()
        await _llm_service.initialize()

    return _llm_service
