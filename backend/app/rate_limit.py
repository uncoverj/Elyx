from fastapi import HTTPException, status

from app.redis_client import redis_client


async def enforce_daily_limit(user_id: int, key_suffix: str, limit: int) -> None:
    key = f"limit:{key_suffix}:{user_id}"
    current = await redis_client.incr(key)
    if current == 1:
        await redis_client.expire(key, 86400)
    if current > limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Daily limit reached")
