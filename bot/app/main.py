import asyncio
import logging

import httpx
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import get_settings
from app.handlers import router


async def _assert_backend_available(base_url: str, retries: int = 20, delay_seconds: float = 1.5) -> None:
    health_url = f"{base_url.rstrip('/')}/health"
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(health_url)
                response.raise_for_status()
                if attempt > 1:
                    logging.info("Backend became available on attempt %s", attempt)
                return
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

    raise RuntimeError(
        "Backend is unreachable. Start backend first (./run_backend.ps1) and verify "
        f"{health_url}"
    ) from last_error


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=logging.INFO)

    if not settings.bot_token.strip():
        raise RuntimeError("BOT_TOKEN is missing. Set BOT_TOKEN in your .env file before starting the bot.")

    await _assert_backend_available(settings.backend_url)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
