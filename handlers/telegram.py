import datetime

from aiogram import F, Router, types
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
import asyncio

from control_db import Database
from keyboards.menu import menu_kb
from handlers.task import check_all_premium

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
        f"Привіт {message.from_user.first_name} 👋,\n"
        "Я 'Помічник рієлтора' створюю пости з olx.ua 🌐\n"
        " • Пришвидшу і полегшу вашу роботу з клієнтами 🔥\n"
        " • Надаю вам можливість безкоштовно 5 раз 🆓\n"
        "скористатися моїми послугами без підписки ✅\n\n"
        "Просто надішліть мені посилання з olx.ua 🔗\n"
        "по продажу чи здачі житла в оренду 🏘\n"
        "І ви отримаєте пост у телеграмі, 💬\n"
        "який використаєте у своїх цілях 🛠\n\n"
        "Приклад поста який ви будете отримувати 📑⬇️",
        reply_markup=menu_kb(),
        disable_web_page_preview=True,
    )

    await asyncio.sleep(7)

    caption = (
        f"🏡1к кв\n"
        f"🏢Поверх: 2 з 11\n"
        f"🔑Площа: 50м2\n"
        f"📍Район: Подільський\n"
        f"💳️ 5000 грн"
        f"\n\nЗаголовок поста олх\n\n"
        f"📝Опис: \nопис який знаходиться під постом на сайті олх"
    )
    media_group = MediaGroupBuilder(caption=caption)
    media_group.add_photo(
        type="photo",
        media=r"https://img.freepik.com/premium-photo/on-a-black-surface-bright-multicolored-stickers-with-the-word-test_380694-1057.jpg?w=1800",
    )
    await message.answer_media_group(media=media_group.build())


@router.message(Command("keyboard"))
async def keyboard(message: Message):
    await message.delete()
    await message.answer("⬇️ Ваша панель з кнопками ⬇️", reply_markup=menu_kb())


@router.message(Command("check"))
async def keyboard(message: Message):
    await message.delete()
    lock = asyncio.Lock()
    await check_all_premium(lock)


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
