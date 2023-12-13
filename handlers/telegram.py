import traceback
import datetime
from aiogram import F, Router, types, Bot
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from olxparser.parser import get_data
from control_db import Database
from keyboards.premium import buy_premium_kb
from keyboards.menu import menu
from aiogram.types import ContentType
from config import PROVIDER_TOKEN

router = Router()


class Edit(StatesGroup):
    phone_number = State()
    control = State()


# ===========================start============================
@router.message(Command("start"))
async def start(message: Message):
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
        expiration = await db.get_expiration_date(telegram_id)
        await message.answer(
            f"👋 Привіт, підписка активна до {expiration}\n"
            "Бажаєте подовжити вашу підписку?",
            reply_markup=buy_premium_kb(True),
            disable_web_page_preview=True,
        )
        return

    await message.answer(
        "Привіт, я парсер для створення постів\n"
        "про здачу квартири в оренду з сайту olx.ua\n\n"
        "Для того щоб скористатися моїми послугами\n"
        "ви повинні придбати платну підписку\n"
        "Приємного користування 😁",
        reply_markup=menu(),
        disable_web_page_preview=True,
    )

    await message.answer(
        "Хочете придбати чи продовжити підписку підписку?",
        reply_markup=buy_premium_kb(False),
        disable_web_page_preview=True,
    )


@router.callback_query(F.data == "Продовжити підписку 💳")
@router.callback_query(F.data == "Придбати підписку 💳")
async def buy_premium(query: CallbackQuery, bot: Bot):
    db = await Database.setup()
    telegram_id = query.from_user.id

    if await db.is_premium_user(telegram_id):
        await query.answer("Підписку продовженно на 30 днів", show_alert=True)

    await query.message.delete()

    await bot.send_invoice(
        chat_id=query.from_user.id,
        title="Підписка на бот для парсингу на 30 днів",
        description=(
            "Придбайте підписку, щоб користуватись \nпослугами цього телеграм боту"
        ),
        payload="Buy premium",
        provider_token=PROVIDER_TOKEN,
        currency="uah",
        prices=[LabeledPrice(label="Ціна за місяць", amount=30000)],
        max_tip_amount=5000,
        suggested_tip_amounts=[1000, 1500, 2500, 5000],
        start_parameter="parsebot",
        provider_data=None,
        photo_url=(
            "https://business.olx.ua/wp-content/uploads/2022/04/fb-image_redesign.png"
        ),
        photo_size=100,
        photo_width=200,
        photo_height=200,
        need_name=True,
        need_phone_number=True,
        need_email=True,
        need_shipping_address=False,
        send_phone_number_to_provider=False,
        send_email_to_provider=False,
        is_flexible=False,
        protect_content=True,
        request_timeout=10,
    )


@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    db = await Database.setup()
    if not await db.is_premium_user(message.from_user.id):
        await message.answer("Дякую за продовження підписки, приємного користування")
        await db.add_premium_user(message.from_user.id)
        return

    await message.answer("Дякую за вашу підписку, ось відео користування")
    await db.add_premium_user(message.from_user.id)


@router.message(F.text.startswith("https://www.olx.ua/"))
async def main(message: Message, state: FSMContext, bot: Bot):
    db = await Database.setup()

    if not await db.is_premium_user(message.from_user.id):
        await message.answer("Придбайте підписку щоб користуватись ботом!")
        return

    try:
        await get_data(message)
    except AttributeError as exeception:
        text_for_admin = (
            f"У користувача {message.from_user.id} сталася помилка\n"
            f"Details: {exeception}\n"
            f"TraceBack: \n\n{traceback.format_exc()}\n"
        )
        await bot.send_message(chat_id=2138964363, text=text_for_admin)
        await message.answer(
            f"Здається пост уже не дійсний 🚫\nАбо виникла якась помилка",
            reply_markup=types.ReplyKeyboardRemove(),
        )


@router.message()
async def all_message(message: Message):
    await message.answer(
        "🔴 Вибачте, але мені потрібне тільки посилання на сторінку olx.ua з"
        " нерухомістю.\nУ форматі https://www.olx.ua/...",
        disable_web_page_preview=True,
    )
