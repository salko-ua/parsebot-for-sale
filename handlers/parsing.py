import traceback
from datetime import datetime
from aiogram import Bot, F, Router
from aiogram.types import Message

from control_db import Database
from olxparser.parser import get_data

router = Router()


@router.message(F.text.startswith("https://www.olx.ua/"))
async def main(message: Message, bot: Bot):
    db = await Database.setup()
    date = datetime.now().timestamp()
    telegram_id = message.from_user.id
    print(((await db.check_count_parsing_post(telegram_id))[0][0]))

    if not await db.is_premium_user(telegram_id):
        if (await db.check_count_parsing_post(telegram_id))[0][0] >= 5:
            await message.answer("Придбайте підписку щоб користуватись ботом!")
            return

    try:
        await get_data(message)
        await db.update_count_parsing_post(telegram_id)
        await db.add_url(telegram_id, url=message.text, date=date)
    except Exception as exeception:
        text_for_admin = (
            f"У користувача {telegram_id} сталася помилка\n"
            f"Details: {exeception}\n"
            f"TraceBack: \n\n{traceback.format_exc()}\n"
        )
        await bot.send_message(chat_id=2138964363, text=text_for_admin)
        await message.answer(f"Здається пост уже не дійсний 🚫")
