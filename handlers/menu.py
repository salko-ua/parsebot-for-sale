from aiogram import F, Router, types, Bot
from aiogram.types import Message
from control_db import Database

router = Router()


@router.message(F.text == "Інформація 🧾")
async def information(message: Message):
    await message.answer()


@router.message(F.text == "Підписка 👑")
async def information(message: Message):
    db = await Database.setup()
    expiration_date = await db.get_expiration_date(message.from_user.id)
    bought_premium = await db.get_bought_premium(message.from_user.id)
    date_purchase = await db.get_date_purchase(message.from_user.id)

    text = (
        "Інформація про вашу підписку 👑\n"
        f"Купував підписку: {bought_premium} раз\n\n"
        f"Дія підписки: <b>{date_purchase}-{expiration_date}</b>"
    )
    
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "Посилання 🔗")
async def information(message: Message):
    await message.answer()


@router.message(F.text == "FAQ 👤")
async def information(message: Message):
    await message.answer()
