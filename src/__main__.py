import asyncio
import sentry_sdk
from aiogram import Dispatcher

from src.config import SENTRY_SDK
from src.middleware import CheckConnectioError, CheckPrivateChat
from src.handlers import admin, menu, parsing, payments, task, telegram

from src.global_variable import bot, dp






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

    await register_handlers(dp)
    await task.create_tasks()
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot Online")
    await dp.start_polling(bot)


async def main():
    try:
        await start_bot()
    except asyncio.CancelledError:
        print("Bot stopped gracefully")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")
