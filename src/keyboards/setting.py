from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def send_settings() -> ReplyKeyboardMarkup | InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    keyboard = ["Змінити групу", "Змінити шаблон"]

    for button in keyboard:
        builder.add(InlineKeyboardButton(text=button, callback_data=button))

    return builder.adjust(1).as_markup(resize_keyboard=True)
