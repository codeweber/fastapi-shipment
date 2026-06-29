from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import ConnectionPool, Redis

from ..settings import cache_settings

def get_redis_connection_pool():
    # Decode responses always, to get str values as str and not bytes
    return ConnectionPool.from_url(cache_settings.get_url(), decode_responses=True)

async def close_redis_connection_pool(pool: ConnectionPool) -> None:
    await pool.aclose()

async def get_redis_connection(request: Request):
    conn = Redis(connection_pool=request.app.state.redis_pool)
    try:
        yield conn
    finally:
        await conn.aclose()

RedisDep = Annotated[Redis, Depends(get_redis_connection)]