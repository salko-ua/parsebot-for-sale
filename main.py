import asyncio, logging
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers import telegram, menu

bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()


async def register_handlers():
    dp.include_router(menu.router)
    dp.include_router(telegram.router)


async def start_bot():
    await register_handlers()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    print("Bot Online")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_bot())
