import traceback
from datetime import datetime
from aiogram import Bot, F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.control_db import Database
from src.olx_api import get_data
from src.keyboards.parsing_edit import edit_parse_advert

router = Router()

class Parser(StatesGroup):
    parser_obj = State()

@router.message(F.text.startswith("https://www.olx.ua"))
@router.message(F.text.startswith("https://olx.ua"))
@router.message(F.text.startswith("https://m.olx.ua"))
async def main(message: Message, bot: Bot, state: FSMContext):
    assert message.from_user is not None
    assert message.text is not None
    db = await Database.setup()
    date = datetime.now().timestamp()
    telegram_id = message.from_user.id

    if not await db.is_premium_user(telegram_id):
        if (await db.check_count_parsing_post(telegram_id))[0][0] >= 5:
            await message.answer("Придбайте підписку щоб користуватись ботом!")
            return

    try:
        parser = await get_data(message)
        await db.update_count_parsing_post(telegram_id)
        await db.add_url(telegram_id, url=message.text, date=date)
        await state.set_state(Parser.parser_obj)
        await state.update_data(parser=parser, message=message)
    except Exception as e:
        text_for_admin = (
            f"У користувача {telegram_id} сталася помилка\n"
            f"Details: {e}\n"
            f"TraceBack: \n\n{traceback.format_exc()}\n"
            f"Посилання: {message.text}"
        )
        await bot.send_message(chat_id=2138964363, text=text_for_admin)
        await message.answer(f"Здається пост уже не дійсний 🚫")
        "Додати шаблон ➕"
        "Репост в канал 🔁"

@router.message(F.text == "Редагувати текст ✏️")
async def edit_caption(message: Message):
    await message.answer("Відправте новий опис для посту")
    
@router.message(F.text, Parser.parser_obj)
async def edit_caption1(message: Message, state: FSMContext):
    data = await state.get_data()
    parser = data.get("parser")

    parser.update_caption(update_to=message.text)
    
    await message.answer_media_group(media=parser.images, caption=parser.full_caption, reply_markup=edit_parse_advert())
    await state.clear()


