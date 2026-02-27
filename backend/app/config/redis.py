import redis.asyncio as aioredis

from app.config.settings import settings

redis_client = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,
)


async def get_redis():
    """Dependency that provides a Redis client."""
    return redis_client
