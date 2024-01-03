import asyncio
import logging

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import TOKEN
from middleware import CheckConnectioError, CheckPrivateChat

bot = Bot(token=TOKEN, parse_mode="HTML")
scheduler = AsyncIOScheduler(timezone="Europe/Kiev")
dp = Dispatcher()

from handlers import admin, menu, parsing, payments, task, telegram


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
    await dp.start_polling(bot)
    print("Bot Online")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_bot())
