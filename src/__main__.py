
import asyncio
import logging
import apykuma
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import TOKEN, SENTRY_SDK, KUMA_TOKEN
from middleware import CheckConnectioError, CheckPrivateChat

bot = Bot(token=TOKEN)
scheduler = AsyncIOScheduler(timezone="Europe/Kiev")
dp = Dispatcher()

from src.handlers import admin, menu, parsing, payments, task, telegram
import sentry_sdk

sentry_sdk.init(
    dsn=SENTRY_SDK,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)


async def register_handlers():
    dp.message.outer_middleware(CheckConnectioError())
    dp.callback_query.outer_middleware(CheckConnectioError())
    dp.message.outer_middleware(CheckPrivateChat())
    dp.callback_query.outer_middleware(CheckPrivateChat())
    dp.include_router(payments.router)
    dp.include_router(admin.router)
    dp.include_router(parsing.router)
    dp.include_router(menu.router)
    dp.include_router(telegram.router)


async def start_bot():
    await register_handlers()
    await task.create_tasks()
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot Online")
    if KUMA_TOKEN != "":
        await apykuma.start(url=KUMA_TOKEN, delay=10)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_bot())
