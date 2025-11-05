"""
Redis client for caching and session management.
"""
import redis.asyncio as aioredis
from typing import Optional, Any
import json
from app.config import get_settings
from app.utils.logger import logger


class RedisClient:
    """Async Redis client wrapper."""

    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[aioredis.Redis] = None

    async def connect(self):
        """Connect to Redis."""
        try:
            self.client = await aioredis.from_url(
                f"redis://{self.settings.redis_host}:{self.settings.redis_port}",
                password=self.settings.redis_password,
                db=self.settings.redis_db,
                encoding="utf-8",
                decode_responses=True,
            )
            await self.client.ping()
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            self.client = None

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
            logger.info("Redis disconnected")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.client:
            return None

        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
    ) -> bool:
        """Set value in cache with optional expiration."""
        if not self.client:
            return False

        try:
            serialized = json.dumps(value)
            if expire:
                await self.client.setex(key, expire, serialized)
            else:
                await self.client.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.client:
            return False

        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False

    async def incr(self, key: str) -> Optional[int]:
        """Increment counter."""
        if not self.client:
            return None

        try:
            return await self.client.incr(key)
        except Exception as e:
            logger.error(f"Redis INCR error: {e}")
            return None

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key."""
        if not self.client:
            return False

        try:
            await self.client.expire(key, seconds)
            return True
        except Exception as e:
            logger.error(f"Redis EXPIRE error: {e}")
            return False


# Global Redis client instance
redis_client = RedisClient()


async def init_redis():
    """Initialize Redis connection."""
    await redis_client.connect()


async def close_redis():
    """Close Redis connection."""
    await redis_client.disconnect()


def get_redis() -> RedisClient:
    """Get Redis client instance."""
    return redis_client
