import asyncio
import logging
from aiogram import Dispatcher
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_bot())
