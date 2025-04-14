from typing import AsyncGenerator

import redis.asyncio as redis
from fastapi import Depends
from src.core.settings import settings


async def init_redis() -> redis.Redis:
    client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=settings.redis_db,
        decode_responses=True,
        health_check_interval=30,
        retry_on_timeout=True,
    )
    return client


redis_client: redis.Redis | None = None


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    global redis_client
    if redis_client is None:
        redis_client = await init_redis()
    yield redis_client


RedisSession = Depends(get_redis)
