import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import get_settings
from app.handlers import router


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=logging.INFO)

    if not settings.bot_token.strip():
        raise RuntimeError("BOT_TOKEN is missing. Set BOT_TOKEN in your .env file before starting the bot.")

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
