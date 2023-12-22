from config import PROVIDER_TOKEN
from control_db import Database

from keyboards.menu import menu, continue_premium
from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery


router = Router()


@router.callback_query(F.data == "Продовжити підписку 💳")
@router.callback_query(F.data == "Придбати підписку 💳")
async def buy_premium(query: CallbackQuery, bot: Bot):
    await query.message.delete()
    await query.answer()

    description = (
        "👑 Підписка на телеграм бота для парсингу\n\n"
        "💸 Тариф: 1 місяць / 300 грн\n\n"
        "🛠 Послуги: Відкриття доступу до парсингу даних про здачу квартир в оренду\n\n"
    )

    await bot.send_invoice(
        chat_id=query.from_user.id,
        title="Оплата підписки",
        description=description,
        payload="Buy premium",
        provider_token=PROVIDER_TOKEN,
        currency="uah",
        prices=[LabeledPrice(label="Ціна за місяць", amount=30000)],
        max_tip_amount=5000,
        suggested_tip_amounts=[1000, 1500, 2500, 5000],
        start_parameter="parsebot",
        provider_data=None,
        need_name=True,
        need_phone_number=True,
        need_email=True,
        need_shipping_address=False,
        send_phone_number_to_provider=False,
        send_email_to_provider=False,
        is_flexible=False,
        protect_content=False,
        request_timeout=10,
    )


@router.pre_checkout_query()
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message):
    await message.delete()
    db = await Database.setup()
    telegram_id = message.from_user.id
    await db.add_premium_user(telegram_id)

    if await db.get_bought_premium(telegram_id) > 1:
        expiration_date = await db.get_expiration_date(telegram_id)
        await message.answer(
            f"Підписку продовженно до {expiration_date}",
            reply_markup=continue_premium(),
        )
        return

    await message.answer(
        "Дякую за вашу підписку, ось відео користування", reply_markup=menu()
    )
