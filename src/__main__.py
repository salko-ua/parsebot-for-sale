import asyncio
import logging
import sentry_sdk

from aiogram import Bot, Dispatcher
from src.config import TOKEN, SENTRY_SDK

bot = Bot(token=TOKEN)
from src.middleware import CheckConnectioError, CheckPrivateChat
from src.handlers import admin, menu, parsing, payments, task, telegram

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


async def register_handlers(dp: Dispatcher):
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
    dp = Dispatcher()

    await register_handlers(dp)
    await task.create_tasks()
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot Online")
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_bot())
