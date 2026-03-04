from datetime import datetime

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models import User
from app.security import validate_tg_init_data


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    tg_init_data: str | None = Header(default=None, alias="tg-init-data"),
    x_service_token: str | None = Header(default=None, alias="x-service-token"),
    x_telegram_id: int | None = Header(default=None, alias="x-telegram-id"),
    x_telegram_username: str | None = Header(default=None, alias="x-telegram-username"),
) -> User:
    settings = get_settings()
    tg_id: int | None = None

    if tg_init_data:
        tg_id = validate_tg_init_data(tg_init_data)
    elif x_service_token == settings.service_token and x_telegram_id:
        tg_id = x_telegram_id

    if not tg_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    result = await db.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(tg_id=tg_id, username=x_telegram_username)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    if x_telegram_username and user.username != x_telegram_username:
        user.username = x_telegram_username
    user.last_active_at = datetime.utcnow()
    await db.commit()
    return user
