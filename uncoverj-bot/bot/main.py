import logging
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from backend.config import settings
from bot.middlewares import RegistrationMiddleware, AntiSpamMiddleware
from bot.handlers import routers

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)


async def on_shutdown(dp: Dispatcher):
    """Graceful shutdown"""
    logger.info("Shutting down bot gracefully...")


async def main():
    logger.info("Starting Uncoverj Bot...")

    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Graceful shutdown
    dp.shutdown.register(on_shutdown)

    # Регистрация Middlewares
    dp.update.outer_middleware(RegistrationMiddleware())
    dp.message.middleware(AntiSpamMiddleware(rate_limit=5, time_window=3.0))

    # Регистрация роутеров
    for router in routers:
        dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot is running!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
