import logging

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

_redis_available: bool | None = None


async def _get_redis():
    global _redis_available
    if _redis_available is False:
        return None
    try:
        from app.redis_client import redis_client
        await redis_client.ping()
        _redis_available = True
        return redis_client
    except Exception:
        if _redis_available is None:
            logger.warning("Redis unavailable — rate limiting disabled for local dev.")
        _redis_available = False
        return None


async def enforce_daily_limit(user_id: int, key_suffix: str, limit: int) -> None:
    client = await _get_redis()
    if client is None:
        return
    key = f"limit:{key_suffix}:{user_id}"
    current = await client.incr(key)
    if current == 1:
        await client.expire(key, 86400)
    if current > limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Daily limit reached")
