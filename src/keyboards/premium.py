from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


def buy_premium_kb(chose: bool) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if chose:
        keyboard = ["Продовжити підписку 💳", "Сховати ❌"]
    else:
        keyboard = ["Придбати підписку 💳", "Сховати ❌"]

    for button in keyboard:
        builder.add(InlineKeyboardButton(text=button, callback_data=button))

    return builder.adjust(1).as_markup(resize_keyboard=True)


def buy_url(
    url: str, order_reference: str
) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="Оплатити", url=url))
    builder.add(
        InlineKeyboardButton(
            text="Передумав ❌",
            callback_data=f"Передумав ❌{order_reference}",
        )
    )

    return builder.adjust(1).as_markup(resize_keyboard=True)


def back() -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    keyboard = ["Відмінити ❌"]

    for button in keyboard:
        builder.add(InlineKeyboardButton(text=button, callback_data=button))

    return builder.adjust(2).as_markup(resize_keyboard=True)
