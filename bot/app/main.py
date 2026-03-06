import asyncio
import logging
import os

import httpx
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import BotCommand
from aiogram.fsm.storage.redis import RedisEventIsolation
from redis.asyncio import Redis

from app.config import get_settings
from app.handlers import router


async def _assert_backend_available(base_url: str, retries: int = 20, delay_seconds: float = 1.5) -> bool:
    health_url = f"{base_url.rstrip('/')}/health"
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(health_url)
                response.raise_for_status()
                if attempt > 1:
                    logging.info("Backend became available on attempt %s", attempt)
                return True
        except httpx.HTTPError as exc:
            last_error = exc
            if attempt < retries:
                logging.warning(
                    "Backend is not ready yet (%s/%s). Retrying in %.1fs...",
                    attempt,
                    retries,
                    delay_seconds,
                )
                await asyncio.sleep(delay_seconds)

    logging.error(
        "Backend health check failed after %s retries: %s",
        retries,
        last_error,
    )
    return False


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if not settings.bot_token.strip():
        raise RuntimeError("BOT_TOKEN is missing. Set BOT_TOKEN in your .env file before starting the bot.")

    logging.info("Starting bot. backend_url=%s", settings.backend_url)
    if os.getenv("RAILWAY_ENVIRONMENT") and settings.backend_url.startswith("http://127.0.0.1"):
        logging.error(
            "BACKEND_URL points to localhost inside Railway. "
            "Set BACKEND_URL=https://elyx-production.up.railway.app in the bot service env vars."
        )
    backend_ok = await _assert_backend_available(settings.backend_url)
    if not backend_ok and settings.strict_backend_check:
        raise RuntimeError(
            "Backend is unreachable and STRICT_BACKEND_CHECK=true. "
            "Set BACKEND_URL correctly or disable strict check."
        )

    redis_client: Redis | None = None
    events_isolation = None
    if settings.redis_url.strip():
        try:
            redis_client = Redis.from_url(settings.redis_url, decode_responses=False)
            await redis_client.ping()
            storage = RedisStorage(redis=redis_client)
            events_isolation = RedisEventIsolation(redis=redis_client)
            logging.info("Using Redis FSM storage: %s", settings.redis_url)
            logging.info("Redis event isolation enabled")
        except Exception as exc:
            logging.warning("Redis storage is unavailable: %s", exc)
            storage = MemoryStorage()
            events_isolation = SimpleEventIsolation()
            redis_client = None
            logging.warning("Falling back to in-process event isolation")
    else:
        storage = MemoryStorage()
        events_isolation = SimpleEventIsolation()
        logging.warning("REDIS_URL is not set. Falling back to in-memory FSM storage.")
        logging.warning("Using in-process event isolation")

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=storage, events_isolation=events_isolation)
    dp.include_router(router)

    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="menu", description="Открыть главное меню"),
        BotCommand(command="profile", description="Моя анкета"),
        BotCommand(command="edit", description="Редактировать анкету"),
        BotCommand(command="find", description="Искать тиммейтов"),
        BotCommand(command="matches", description="Мои мэтчи"),
        BotCommand(command="settings", description="Настройки"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="support", description="Поддержка"),
        BotCommand(command="reset", description="Сбросить анкету"),
        BotCommand(command="app", description="Открыть Elyx App"),
    ]

    # Clear stale webhook when running polling mode (common reason for silent non-response).
    await bot.delete_webhook(drop_pending_updates=settings.drop_pending_updates)
    await bot.set_my_commands(commands)
    me = await bot.get_me()
    logging.info("Bot connected as @%s (%s)", me.username, me.id)
    logging.info("Polling started")

    if not backend_ok:
        logging.warning(
            "Bot is online, but backend is unavailable. Commands that require API calls may fail "
            "until BACKEND_URL becomes reachable."
        )

    try:
        await dp.start_polling(bot)
    finally:
        if redis_client is not None:
            await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
