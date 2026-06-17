import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from app.config import config
from app.database.db import db
from app.handlers import start, cases, leaderboard, profile, topup
from app.web.app import create_web_app

# Enable logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# Include routers
dp.include_router(start.router)
dp.include_router(cases.router)
dp.include_router(leaderboard.router)
dp.include_router(profile.router)
dp.include_router(topup.router)

# HTTP port: Render injects PORT; default 8080 locally
HTTP_PORT = int(os.getenv("PORT", 8080))


async def set_default_commands():
    """Set default bot commands"""
    commands = [
        BotCommand(command="start", description="🎮 Начать игру"),
        BotCommand(command="stats", description="📊 Моя статистика"),
        BotCommand(command="help", description="ℹ️ Справка"),
    ]
    await bot.set_my_commands(commands)


async def on_startup():
    """Startup handler"""
    logger.info("Bot starting...")
    await db.initialize()
    await set_default_commands()
    logger.info("Bot started!")


async def on_shutdown():
    """Shutdown handler"""
    logger.info("Bot shutting down...")
    await db.close()
    logger.info("Bot stopped!")


async def main():
    """Main: run HTTP server (Mini App + API) and bot polling in parallel."""
    await on_startup()

    # Build aiohttp app with Mini App routes
    http_app = create_web_app()
    runner = web.AppRunner(http_app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=HTTP_PORT)
    await site.start()
    logger.info(f"HTTP server (Mini App + API) listening on :{HTTP_PORT}")

    try:
        logger.info("Bot polling started...")
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()
        await on_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
