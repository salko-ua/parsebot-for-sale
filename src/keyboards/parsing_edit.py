
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder



def edit_parse_advert(template: bool = False) -> ReplyKeyboardMarkup | InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    keyboard = [
        "🔖 Допомога",
        "🔄 Cкинути",
        "✏️ Редагувати",
        "➕ Додати шаблон" if not template else "➖ Видалити шаблон",
        "✅ Завершити",
        "🔁 Репост в канал"
    ]

    for button in keyboard:
        builder.add(InlineKeyboardButton(text=button, callback_data=button))

    return builder.adjust(2).as_markup(resize_keyboard=True)




