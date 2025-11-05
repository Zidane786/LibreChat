"""
Rate limiting middleware.
"""
from fastapi import Request, HTTPException, status
from typing import Callable
import time
from app.utils.redis_client import get_redis
from app.config import get_settings
from app.utils.logger import logger


class RateLimiter:
    """Rate limiter using Redis."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis = get_redis()

    async def check_rate_limit(
        self,
        identifier: str,
    ) -> tuple[bool, int, int]:
        """
        Check if request is within rate limit.

        Args:
            identifier: Unique identifier (IP, user ID, etc.)

        Returns:
            Tuple of (is_allowed, current_count, reset_time)
        """
        key = f"rate_limit:{identifier}"
        current_time = int(time.time())

        # Get current count
        count = await self.redis.incr(key)

        if count == 1:
            # First request in window, set expiration
            await self.redis.expire(key, self.window_seconds)

        # Calculate reset time
        ttl = self.window_seconds
        reset_time = current_time + ttl

        # Check if over limit
        is_allowed = count <= self.max_requests

        return is_allowed, count, reset_time


async def rate_limit_middleware(
    request: Request,
    call_next: Callable,
    max_requests: int = 100,
    window_seconds: int = 60,
):
    """
    Rate limiting middleware.

    Args:
        request: FastAPI request
        call_next: Next middleware/handler
        max_requests: Max requests allowed
        window_seconds: Time window

    Raises:
        HTTPException: If rate limit exceeded
    """
    settings = get_settings()

    # Skip if rate limiting disabled
    if not settings.rate_limit_enabled:
        return await call_next(request)

    # Get identifier (IP address or user ID)
    identifier = request.client.host if request.client else "unknown"

    # If user is authenticated, use user ID
    if hasattr(request.state, "user") and request.state.user:
        identifier = request.state.user.id

    # Check rate limit
    limiter = RateLimiter(max_requests, window_seconds)
    is_allowed, current_count, reset_time = await limiter.check_rate_limit(identifier)

    # Add rate limit headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(max_requests)
    response.headers["X-RateLimit-Remaining"] = str(max(0, max_requests - current_count))
    response.headers["X-RateLimit-Reset"] = str(reset_time)

    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time),
            },
        )

    return response
