import traceback
from datetime import datetime
from aiogram import Bot, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.control_db import Database
from src.olx_api import get_data, Parser
from src.keyboards.parsing_edit import edit_parse_advert

router = Router()

class ParserState(StatesGroup):
    edit_caption = State()
    buttons = State()

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
        await state.set_state(ParserState.buttons)
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

@router.callback_query(F.data == "➕ Додати шаблон", ParserState.buttons)
async def add_template(query: CallbackQuery, state: FSMContext):
    db = await Database.setup()
    template = await db.get_template(telegram_id=query.from_user.id)

    if template is None or template == "":
        await query.answer("Ви ще не маєте шаблону додайте його в налаштуваннях", show_alert=True)
        return
  
    data: dict = await state.get_data()
    parser: Parser = data.get("parser")

    parser.update_template(update_to=template)
    
    await query.message.edit_caption(caption=parser.full_caption)
    await query.message.edit_reply_markup(reply_markup=edit_parse_advert(template=True))

@router.callback_query(F.data == "➖ Видалити шаблон", ParserState.buttons)
async def delete_template(query: CallbackQuery, state: FSMContext):
    data: dict = await state.get_data()
    parser: Parser = data.get("parser")

    parser.update_template(update_to="")
    
    await query.message.edit_caption(caption=parser.full_caption)
    await query.message.edit_reply_markup(reply_markup=edit_parse_advert(template=False))

    
@router.callback_query(F.data == "✏️ Редагувати", ParserState.buttons)
async def edit_caption(query: CallbackQuery, state: FSMContext):
    data: dict = await state.get_data()
    parser: Parser = data.get("parser")

    
    await query.answer("Тепер надішліть відредаговний текст", show_alert=True)
    await query.message.delete()
    await query.message.answer(parser.header + "\n\n" + parser.caption)
    await state.set_state(ParserState.edit_caption)

@router.callback_query(F.data == "🔖 Допомога", ParserState.buttons)
async def help(query: CallbackQuery):
    alert = (
        f"✏️ Редагувати-\n"
        f"Редагує заголовок та опис в пост\n"
        f"🔄 Cкинути-\n"
        f"Повертає до початку\n"
        f"➕Додати шаблон-\n"
        f"Додає ваш шаблон в пост\n"
        f"✅ Завершити або 🔁 Репост в канал\n"
        f"Надсилає готовий пост\n"
)
    await query.answer(text=alert, show_alert=True)
    
@router.message(F.text, ParserState.edit_caption)
async def edit_caption1(message: Message, state: FSMContext):
    assert message.text is not None
    data: dict = await state.get_data()
    parser: Parser = data.get("parser")
    
    parser.update_header(update_to=message.text)
    parser.update_caption(update_to="")
    
    message = await message.answer_photo(photo=parser.images[0].media, caption=parser.full_caption, reply_markup=edit_parse_advert())
    await state.set_state(ParserState.buttons)




@router.callback_query(F.data == "🔄 Cкинути", ParserState.buttons)
async def reset(query: CallbackQuery, state: FSMContext):
    data: dict = await state.get_data()
    parser: Parser = data.get("parser")
    parser.reset_all()
    
    await query.message.delete()
    await query.message.answer_photo(photo=parser.images[0].media, caption=parser.full_caption, reply_markup=edit_parse_advert())

@router.callback_query(F.data == "✅ Отримати пост", ParserState.buttons)
async def finish(query: CallbackQuery, state: FSMContext):
    data: dict = await state.get_data()
    parser: Parser = data.get("parser")
    await state.clear()

    await query.message.answer_media_group(media=parser.images)
    await query.answer("Пост відредаговано ✅", show_alert=True)

    await query.message.delete()

@router.callback_query(F.data == "🔁 Репост в канал", ParserState.buttons)
async def repost_to_group(query: CallbackQuery, state: FSMContext):
    db = await Database.setup()
    group_id = await db.get_group_id(telegram_id=query.from_user.id)

    if group_id == 0 or group_id is None:
        await query.answer("Ви не приєднали каналу", show_alert=True)
        return

    data: dict = await state.get_data()
    parser: Parser = data.get("parser")
    
    try:
        await query.message.bot.send_media_group(chat_id=group_id, media=parser.images)
        await query.answer("Пост надіслано в канал ✅", show_alert=True)
        await state.clear()
        await query.message.delete()
    except Exception as e:
        await query.answer("Перевірте чи правильний id каналу/групи який ви приєднали та чи має бот права адміністратора", show_alert=True)
    

