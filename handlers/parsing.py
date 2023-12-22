import traceback
from datetime import datetime
from aiogram import F, Router, Bot
from aiogram.types import Message
from olxparser.parser import get_data
from control_db import Database
from urllib.parse import urlparse

router = Router()


@router.message(F.text.startswith("https://www.olx.ua/"))
async def main(message: Message, bot: Bot):
    db = await Database.setup()
    date = datetime.now().timestamp()

    if not await db.is_premium_user(message.from_user.id):
        await message.answer("Придбайте підписку щоб користуватись ботом!")
        return

    try:
        await get_data(message)
        await db.add_url(message.from_user.id, url=message.text, date=date)
    except Exception as exeception:
        text_for_admin = (
            f"У користувача {message.from_user.id} сталася помилка\n"
            f"Details: {exeception}\n"
            f"TraceBack: \n\n{traceback.format_exc()}\n"
        )
        await bot.send_message(chat_id=2138964363, text=text_for_admin)
        await message.answer(f"Здається пост уже не дійсний 🚫")
