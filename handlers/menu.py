from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from control_db import Database
from aiogram.filters.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from keyboards.premium import back
from keyboards.menu import hide_kb, continue_premium

router = Router()


class SendFAQ(StatesGroup):
    send_message = State()


@router.message(F.text == "Інформація 🧾")
async def information(message: Message):
    await message.answer(
        r"""<b><a href = "https://telegra.ph/Pol%D1%96tika-konf%D1%96denc%D1%96jnost%D1%96-12-20">Політика конфіденційності</a></b>""",
        parse_mode="HTMl",
        disable_web_page_preview=True,
    )
    await message.answer(
        r"""<b><a href = "https://telegra.ph/DOGOV%D0%86R-OFERTI-12-20">Договір Оферти</a></b>""",
        parse_mode="HTMl",
        disable_web_page_preview=True,
    )


@router.message(F.text == "Підписка 👑")
async def premium(message: Message):
    await message.delete()
    db = await Database.setup()
    telegram_id = message.from_user.id

    if not await db.telegram_id_premium_exists(telegram_id):
        await message.answer(
            text=(
                f"Інформація про вашу підписку 👑\n"
                f"Підписка: не активна ❌\n"
                f"Купував підписку: 0 раз"
            ),
            reply_markup=hide_kb(),
        )
        return

    is_premium = await db.is_premium_user(telegram_id)
    expiration_date = await db.get_expiration_date(telegram_id)
    bought_premium = await db.get_bought_premium(telegram_id)
    date_purchase = await db.get_date_purchase(telegram_id)

    if is_premium:
        text = (
            f"Інформація про вашу підписку 👑\n"
            f"Підписка: активна ✅\n"
            f"Купував підписку: {bought_premium} раз\n\n"
            f"Дія підписки до: <b>{date_purchase}-{expiration_date}</b>"
        )
    elif not is_premium:
        text = (
            f"Інформація про вашу підписку 👑\n"
            f"Підписка: не активна ❌\n"
            f"Купував підписку: {bought_premium} раз\n\n"
            f"Закінчилась: <b>{expiration_date}</b>"
        )

    await message.answer(text, parse_mode="HTML", reply_markup=continue_premium())


@router.message(F.text == "Посилання 🔗")
async def faq(message: Message):
    await message.delete()
    db = await Database.setup()

    if not await db.is_premium_user(message.from_user.id):
        await message.answer("Придбайте підписку, щоб переглядати останні посилання 😕")
        return

    urls = await db.see_urls(message.from_user.id)
    if len(urls) > 0:
        text = "Останні 10 посилань: \n"
        s = 1
        for url in urls:
            text += f"{s}. {url[0]}\n"
            s += 1
    else:
        text = "Ви не зпарсили жодного поста 😐"

    await message.answer(text, disable_web_page_preview=True, reply_markup=hide_kb())


@router.message(F.text == "FAQ 👤")
async def information(message: Message, state: FSMContext):
    await message.delete()
    db = await Database.setup()

    if not await db.is_premium_user(message.from_user.id):
        await message.answer(
            "Щоб написати адміну у вас повинна бути активна підписка 🥹"
        )
        return

    message = await message.answer(
        "Напишіть нижче питання, і воно буде відправлене до адміна", reply_markup=back()
    )
    await state.set_state(SendFAQ.send_message)
    await state.update_data(message=message)


@router.callback_query(F.data == "Відмінити ❌", SendFAQ.send_message)
async def faq_back(query: CallbackQuery, state: FSMContext):
    await state.clear()
    await query.message.delete()


@router.message(SendFAQ.send_message)
async def faq_back(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    messages: Message = data["message"]

    await state.clear()
    text_from_user = (
        f"Користувач {message.from_user.id}\n"
        "Надіслав повідомлення: \n"
        f"{message.text}"
    )

    await bot.send_message(-1001902595324, message_thread_id=348, text=text_from_user)

    await messages.delete()
    await message.answer("Повідомлення успішно надіслано ✅\nОчікуйте на відповідь 🕐")
