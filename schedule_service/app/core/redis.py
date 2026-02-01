from redis.asyncio import Redis, from_url

from app.core.config import settings

redis_client: Redis = None

async def init_redis() -> None:
    global redis_client
    redis_client = await from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True
    )


async def close_redis() -> None:
    if redis_client:
        await redis_client.close()


async def get_redis() -> Redis:
    return redis_client