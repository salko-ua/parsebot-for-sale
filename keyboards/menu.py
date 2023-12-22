from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    keyboard = ["Інформація 🧾", "Підписка 👑", "Посилання 🔗", "FAQ 👤"]

    for button in keyboard:
        builder.add(KeyboardButton(text=button, callback_data=button))

    return builder.adjust(2).as_markup(resize_keyboard=True)


def hide_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    keyboard = ["Сховати ❌"]

    for button in keyboard:
        builder.add(InlineKeyboardButton(text=button, callback_data=button))

    return builder.adjust(2).as_markup(resize_keyboard=True)


def continue_premium() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    keyboard = ["Продовжити підписку 💳", "Сховати ❌"]

    for button in keyboard:
        builder.add(InlineKeyboardButton(text=button, callback_data=button))

    return builder.adjust(1).as_markup(resize_keyboard=True)
