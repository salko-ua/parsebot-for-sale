from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def menu_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    keyboard = ["Інформація 🧾", "Підписка 👑", "Посилання 🔗", "FAQ 👤"]

    for button in keyboard:
        builder.add(KeyboardButton(text=button, callback_data=button))

    return builder.adjust(2).as_markup(resize_keyboard=True)


def about(without: str = "") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    keyboard = [
        "Політика конфід. 🔐",
        "Договір Оферти 📑",
        "Тариф 💸",
        "Про нас 👥",
        "Поради користування ❤️",
        "Контакти 📱",
        "Сховати ❌",
    ]

    # if without != "":
    #     keyboard.remove(without)

    for button in keyboard:
        builder.add(InlineKeyboardButton(text=button, callback_data=button))

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


def buy_premium() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    keyboard = ["Придбати підписку 💳", "Сховати ❌"]

    for button in keyboard:
        builder.add(InlineKeyboardButton(text=button, callback_data=button))

    return builder.adjust(1).as_markup(resize_keyboard=True)
