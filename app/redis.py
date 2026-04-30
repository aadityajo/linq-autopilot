from fastapi import Depends
from redis.asyncio import Redis
from app.internals.redisClient import redis_client


async def get_redis() -> Redis:
    return redis_client.get_client()
