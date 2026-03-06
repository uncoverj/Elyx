import asyncio
import logging

import httpx
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

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
    logging.basicConfig(level=logging.INFO)

    if not settings.bot_token.strip():
        raise RuntimeError("BOT_TOKEN is missing. Set BOT_TOKEN in your .env file before starting the bot.")

    logging.info("Starting bot. backend_url=%s", settings.backend_url)
    backend_ok = await _assert_backend_available(settings.backend_url)
    if not backend_ok and settings.strict_backend_check:
        raise RuntimeError(
            "Backend is unreachable and STRICT_BACKEND_CHECK=true. "
            "Set BACKEND_URL correctly or disable strict check."
        )

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    # Clear stale webhook when running polling mode (common reason for silent non-response).
    await bot.delete_webhook(drop_pending_updates=settings.drop_pending_updates)
    me = await bot.get_me()
    logging.info("Bot connected as @%s (%s)", me.username, me.id)

    if not backend_ok:
        logging.warning(
            "Bot is online, but backend is unavailable. Commands that require API calls may fail "
            "until BACKEND_URL becomes reachable."
        )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
