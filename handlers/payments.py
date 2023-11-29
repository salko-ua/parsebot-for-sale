from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from aiogram import Bot, Router, types
from config import PROVIDER_TOKEN

async def order(message: Message, bot: Bot):
    await bot.send_invoice(
        chat_id=message.from_user.id,
        title="Підписка premium на parsebot",
        description="Придбайте підписку, щоб користуватись \nпослугами цього телеграм боту",
        payload="Buy premium",
        provider_token=PROVIDER_TOKEN,
        currency="uah",
        prices=[
            LabeledPrice(
                label="Ціна за місяць",
                amount=5000
            )
        ],
        max_tip_amount=5000,
        suggested_tip_amounts=[1000, 1500, 2500, 5000],
        start_parameter="parsebot",
        provider_data=None,
        photo_url="https://business.olx.ua/wp-content/uploads/2022/04/fb-image_redesign.png",
        need_name=True,
        need_phone_number=True,
        need_email=True,
        need_shipping_address=False,
        send_phone_number_to_provider=False,
        send_email_to_provider=False,
        is_flexible=False,
        protect_content=True,
        request_timeout=10
    )