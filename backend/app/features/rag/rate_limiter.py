# backend/app/features/rag/rate_limiter.py
"""Rate limiter for RAG API endpoints."""

import time
from collections import defaultdict
from typing import Dict, Optional, Tuple

from app.core.config import settings
from app.core.exceptions import RateLimitError
from app.core.observability import logs


class RateLimiter:
    """Token bucket rate limiter for session-based rate limiting."""

    def __init__(
        self,
        max_requests: int = None,
        window_seconds: int = None,
    ):
        self.max_requests = max_requests or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_WINDOW
        self._buckets: Dict[str, list] = defaultdict(list)

    def _cleanup_old_requests(self, key: str, current_time: float) -> None:
        """Remove requests outside the current window."""
        cutoff = current_time - self.window_seconds
        self._buckets[key] = [
            (ts, count) for ts, count in self._buckets[key] if ts > cutoff
        ]

    def _get_request_count(self, key: str) -> int:
        """Get total request count in current window."""
        return sum(count for _, count in self._buckets[key])

    async def check(self, key: str) -> Tuple[bool, int]:
        """Check if key is within rate limit."""
        current_time = time.time()
        self._cleanup_old_requests(key, current_time)
        request_count = self._get_request_count(key)
        remaining = self.max_requests - request_count
        return remaining > 0, max(0, remaining)

    async def record(self, key: str) -> None:
        """Record a request."""
        current_time = time.time()
        self._buckets[key].append((current_time, 1))

    async def check_and_record(self, key: str) -> int:
        """Check rate limit and record request if allowed."""
        is_allowed, remaining = await self.check(key)

        if not is_allowed:
            logs.security(
                "Rate limit exceeded",
                "rate_limit",
                metadata={
                    "key": key,
                    "limit": self.max_requests,
                    "window": self.window_seconds,
                },
            )
            raise RateLimitError(
                f"Rate limit exceeded. Try again in {self.window_seconds} seconds."
            )

        await self.record(key)
        return remaining - 1


_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get the rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
