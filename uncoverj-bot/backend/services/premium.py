"""
Premium-сервис: логика подписки и проверки статуса.
"""
from datetime import datetime, timedelta
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.user import User

# Тарифы Premium (в Telegram Stars)
PREMIUM_PLANS = {
    "1_week": {"label": "1 неделя", "stars": 100, "days": 7},
    "1_month": {"label": "1 месяц", "stars": 350, "days": 30},
    "3_months": {"label": "3 месяца", "stars": 900, "days": 90},
}


async def activate_premium(session: AsyncSession, user_id: int, plan_key: str) -> bool:
    """Активировать Premium на указанный тариф"""
    plan = PREMIUM_PLANS.get(plan_key)
    if not plan:
        return False

    user = await session.get(User, user_id)
    if not user:
        return False

    # Если Premium уже активен, продлеваем
    now = datetime.utcnow()
    if user.premium_until and user.premium_until > now:
        new_until = user.premium_until + timedelta(days=plan["days"])
    else:
        new_until = now + timedelta(days=plan["days"])

    await session.execute(
        update(User).where(User.id == user_id).values(
            is_premium=True,
            premium_until=new_until
        )
    )
    await session.commit()
    return True


def is_premium_active(user: User) -> bool:
    """Проверить, активен ли Premium"""
    if not user.is_premium:
        return False
    if user.premium_until and user.premium_until < datetime.utcnow():
        return False
    return True
