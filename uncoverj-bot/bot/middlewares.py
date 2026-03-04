"""
Middleware: антиспам и проверка регистрации.
"""
import time
from typing import Callable, Dict, Any, Awaitable
from collections import defaultdict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from sqlalchemy import select, update, func

from backend.database import async_session_maker
from backend.models.user import User
from backend.models.profile import Profile


class RegistrationMiddleware(BaseMiddleware):
    """
    Проверяет, зарегистрирован ли пользователь.
    Результат прокидывается в handlers через data['db_user'] и data['has_profile'].
    """
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        if not event.from_user:
            return await handler(event, data)

        user_tg_id = event.from_user.id

        async with async_session_maker() as session:
            stmt = select(User).where(User.telegram_id == user_tg_id)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            has_profile = False
            if user:
                # Обновляем last_seen
                await session.execute(
                    update(User).where(User.id == user.id).values(last_seen=func.now())
                )
                # Проверяем профиль
                prof_stmt = select(Profile).where(Profile.user_id == user.id)
                prof_res = await session.execute(prof_stmt)
                if prof_res.scalar_one_or_none():
                    has_profile = True

                await session.commit()

        data['db_user'] = user
        data['has_profile'] = has_profile

        return await handler(event, data)


class AntiSpamMiddleware(BaseMiddleware):
    """
    Антиспам: ограничение количества сообщений от одного пользователя.
    Лимит: 5 сообщений в 3 секунды.
    """
    def __init__(self, rate_limit: int = 5, time_window: float = 3.0):
        super().__init__()
        self.rate_limit = rate_limit
        self.time_window = time_window
        # {user_id: [timestamp1, timestamp2, ...]}
        self._user_timestamps: Dict[int, list] = defaultdict(list)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        user_id = event.from_user.id
        now = time.time()

        # Очистка старых таймстампов
        self._user_timestamps[user_id] = [
            ts for ts in self._user_timestamps[user_id]
            if now - ts < self.time_window
        ]

        if len(self._user_timestamps[user_id]) >= self.rate_limit:
            await event.answer("⚠️ Слишком много сообщений! Подожди немного.")
            return

        self._user_timestamps[user_id].append(now)
        return await handler(event, data)
