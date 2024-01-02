import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from control_db import Database
from keyboards.menu import menu_kb

router = Router()


# ===========================start============================
@router.message(Command("start"))
async def start(message: Message):
    await message.delete()
    db = await Database.setup()
    telegram_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username
    date_join = datetime.datetime.now()

    exists = await db.telegram_id_exists(telegram_id=telegram_id)
    exists_premium = await db.is_premium_user(telegram_id=telegram_id)
    if not exists:
        await db.add_user(telegram_id, first_name, username, date_join)

    if exists_premium:
        expiration_date = await db.get_expiration_date(telegram_id)
        await message.answer(
            f"👋 Привіт, підписка активна до {expiration_date}\n"
            "Бажаєте подовжити вашу підписку?",
            reply_markup=menu_kb(),
            disable_web_page_preview=True,
        )
        return

    await message.answer(
        "Привіт, я парсер для створення постів з сайту olx.ua\n"
        "Для того щоб користуватися моїми послугами\n"
        "ви повинні придбати платну підписку ⬇️\n\n"
        "Також ви можете спробувати бота без підписки\n"
        "Для цього ви повинні надіслати йому посилання\n"
        "У вас є всього одне тестове посилання\n"
        "Яке буде використанно, далі потрібно придбати підписку\n",
        reply_markup=menu_kb(),
        disable_web_page_preview=True,
    )


@router.message(Command("keyboard"))
async def keyboard(message: Message):
    await message.delete()
    await message.answer("⬇️ Ваша панель з кнопками ⬇️", reply_markup=menu_kb())


@router.callback_query(F.data == "Сховати ❌")
async def hide(query: CallbackQuery):
    await query.message.delete()


@router.message()
async def all_message(message: Message):
    if message.chat.type == "private":
        text = (
            "🔴 Вибачте, але мені потрібне тільки посилання на сторінку olx.ua з"
            " нерухомістю.\nУ форматі https://www.olx.ua/..."
        )

        await message.answer(text, disable_web_page_preview=True)
