from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def buy_premium_kb(chose: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if chose:
        keyboard = ["Продовжити підписку 💳"]
    else:
        keyboard = ["Придбати підписку 💳"]

    for button in keyboard:
        builder.add(InlineKeyboardButton(text=button, callback_data=button))

    return builder.adjust(2).as_markup(resize_keyboard=True)
