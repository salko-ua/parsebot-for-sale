import asyncio

from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMINS
from control_db import Database
from keyboards.admin import admin_kb, send_alarm
from keyboards.menu import hide_kb
from main import bot
from datetime import datetime

router = Router()


class SendNews(StatesGroup):
    send_message = State()
    send_message_finish = State()
    send_news_users = State()
    send_news_premium = State()


@router.message(F.text == "db")
async def send_file_db(message: Message):
    if not (message.from_user.id in ADMINS):
        return

    file_path = types.FSInputFile("data/database.db")
    await bot.send_document(message.from_user.id, file_path)


@router.message(Command("admin"))
async def admin(message: Message):
    if message.from_user.id in ADMINS:
        await message.delete()
        await message.answer("Ось ваша клавіатура ⬇️", reply_markup=admin_kb())


@router.message(F.text == "Люди 👥")
async def people_ex(message: Message):
    if not message.from_user.id in ADMINS:
        return

    db = await Database.setup()
    all_users = await db.get_all_user()
    premium_users = await db.get_all_premium_telegram_id()

    new = "Користувачі які ні разу не купували преміум:"

    for telegram_id, username, date_join in all_users[0]:
        if telegram_id not in premium_users[0]:
            data = datetime.strptime(date_join, "%d.%m.%Y %H:%M")
            formatted_date = data.strftime("%d.%m.%Y %H:%M")
            new += f"\nІм`я: @{username}\nID: {telegram_id}\nДата приєднання{formatted_date}"

    await message.answer()


@router.message(F.text == "Статистика 📊")
async def stats(message: Message):
    await message.delete()
    if not message.from_user.id in ADMINS:
        return

    db = await Database.setup()
    operations = await db.get_stats_from_operation()
    operation_1day = await db.get_stats_from_operation(1)
    operation_7days = await db.get_stats_from_operation(7)
    operation_30days = await db.get_stats_from_operation(30)

    stats_all_time = {"count": operations[0], "sum": operations[1]}
    stats_1day = {"count": operation_1day[0], "sum": operation_1day[1]}
    stats_7day = {"count": operation_7days[0], "sum": operation_7days[1]}
    stats_30day = {"count": operation_30days[0], "sum": operation_30days[1]}
    zero = "0"

    generated_message = (
        f"Статистика по боту 📊:\n"
        f"Загальна к-ть користувачів: {await db.get_count_users()}\n"
        f"К-ть користувачів з активною підпискою: {await db.get_count_premium_user(1)}\n"
        f"К-ть користувачів які не продовжили підписку: {await db.get_count_premium_user(0)}\n"
        f"К-ть користувачів які хоч раз купували підписку: {await db.get_count_premium_user(1) + await db.get_count_premium_user(0)}\n\n"
        f"Статистика по доходу 📊:\n"
        f"День:\n"
        f"К-ть покупок - {stats_1day['count']}\n"
        f"Зароблено грошей - {stats_1day['sum'] if stats_1day['sum'] else zero}\n\n"
        f"Тиждень:\n"
        f"К-ть покупок - {stats_7day['count']}\n"
        f"Зароблено грошей - {stats_7day['sum'] if stats_7day['sum'] else zero}\n\n"
        f"Місяць:\n"
        f"К-ть покупок - {stats_30day['count']}\n"
        f"Зароблено грошей - {stats_30day['sum'] if stats_30day['sum'] else zero}\n\n"
        f"За весь час:\n"
        f"К-ть покупок - {stats_all_time['count']}\n"
        f"Зароблено грошей - {stats_all_time['sum'] if stats_all_time['sum'] else zero}\n\n"
    )

    await message.answer(text=generated_message, reply_markup=hide_kb())


@router.message(F.text == "Розсилка 📢")
async def alarm(message: Message):
    if not message.from_user.id in ADMINS:
        return

    text = "Кому написати? 🤔\nОсобисто 👤\nВсім користувачам👥\nПреміум користувачам👑"
    await message.delete()
    await message.answer(text, reply_markup=send_alarm())


@router.callback_query(F.data == "Всім 👥")
async def send_alarm_all(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer("Напишіть повідомлення: ")
    await state.set_state(SendNews.send_news_users)


@router.callback_query(F.data == "Особисто 👤")
async def send_alarm_single(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer("Напишіть повідомлення: ")
    await state.set_state(SendNews.send_message)


@router.message(SendNews.send_message, F.text)
async def send_message_single(message: Message, state: FSMContext):
    await state.set_state(SendNews.send_message_finish)
    await state.update_data(message=message.text)
    await message.answer("Напишіть telegram_id: ")


@router.message(SendNews.send_message_finish, F.text)
async def send_mixed_news2(message: Message, state: FSMContext):
    data = await state.get_data()
    message_text = data["message"]
    await state.clear()
    try:
        await bot.send_message(
            chat_id=message.text, text=f"Адміністратор бота написав: \n{message_text}"
        )
        await message.answer("Повідомлення надісланно")
    except:
        await message.answer("Користувача не знайдено!")


@router.callback_query(F.data == "Преміум 👑")
async def send_alarm_premium(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer("Напишіть повідомлення: ")
    await state.set_state(SendNews.send_news_premium)


@router.message(SendNews.send_news_premium, F.text)
async def send_mixed_news2(message: Message, state: FSMContext):
    db = await Database.setup()
    await state.clear()

    premium_user_ids = map(lambda e: e[0], await db.get_all_premium_telegram_id())

    if not premium_user_ids:
        await message.answer("Немає людей з підпискою")
        return

    await asyncio.gather(*map(send_notification(message.text), premium_user_ids))

    await message.answer("Надсилання закінчено!")


@router.message(SendNews.send_news_users, F.text)
async def send_mixed_news2(message: Message, state: FSMContext):
    db = await Database.setup()
    await state.clear()

    user_ids = map(lambda e: e[0], await db.get_all_user_telegram_id())

    if not user_ids:
        await message.answer("у боті немає людей")
        return

    await asyncio.gather(*map(send_notification(message.text), user_ids))

    await message.answer("Надсилання закінчено!")


def send_notification(text: str):
    async def wrapped(user_id: int):
        try:
            await bot.send_message(user_id, text)
        except:
            pass

    return wrapped
