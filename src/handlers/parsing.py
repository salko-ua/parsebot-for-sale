import traceback
from datetime import datetime
from aiogram import Bot, F, Router
from aiogram.types import Message

from src.database import Database
from src.parser.parser import get_data

router = Router()


@router.message(F.text.startswith("https://www.olx.ua/"))
@router.message(F.text.startswith("https://olx.ua/"))
@router.message(F.text.startswith("https://m.olx.ua/"))
async def main(message: Message, bot: Bot):
    db = await Database.setup()
    date = datetime.now().timestamp()
    telegram_id = message.from_user.id

    if not await db.is_premium_user(telegram_id):
        if (await db.check_count_parsing_post(telegram_id))[0][0] >= 5:
            await message.answer("Придбайте підписку щоб користуватись ботом!")
            return

    try:
        await get_data(message)
        await db.update_count_parsing_post(telegram_id)
        await db.add_url(telegram_id, url=message.text, date=date)
    except Exception as e:
        text_for_admin = (
            f"У користувача {telegram_id} сталася помилка\n"
            f"Details: {e}\n"
            f"TraceBack: \n\n{traceback.format_exc()}\n"
            f"Посилання: {message.text}"
        )
        await bot.send_message(chat_id=2138964363, text=text_for_admin)
        await message.answer(f"Здається пост уже не дійсний 🚫")
