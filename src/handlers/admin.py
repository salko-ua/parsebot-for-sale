import asyncio
import traceback
from pathlib import Path
from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.config import ADMINS
from src.control_db import Database
from src.keyboards.admin import admin_kb, send_alarm
from src.keyboards.menu import hide_kb
from datetime import datetime
from src.handlers.payments import generate_random_string

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
    await message.bot.send_document(message.from_user.id, file_path)


@router.message(F.text == "db_migrate")
async def migrate_db(message: Message):
    if message.from_user.id not in ADMINS:
        return

    db = await Database.setup()
    result = await db.migrate1()
    await message.answer(result)


@router.message(Command("admin"))
async def admin(message: Message):
    if message.from_user.id in ADMINS:
        await message.delete()
        await message.answer("Ось ваша клавіатура ⬇️", reply_markup=admin_kb())


@router.message(F.text.startswith("add"))
async def add_fucking_stupid_people(message: Message):
    if message.from_user.id not in ADMINS:
        return

    db = await Database.setup()
    data = message.text.split()

    await db.add_premium_user(data[1])
    await db.update_premium_operations(
        telegram_id=int(data[1]),
        message_id=message.message_id,
        order_reference=generate_random_string(12),
        order_date=int(datetime.now().replace(hour=0, minute=0, second=0).timestamp()),
        reason_code=1100,
        transaction_status="Approved",
        price=int(data[2]),
    )

    # [N] NOTIFY ADMINISTRATOR
    await message.bot.send_message(
        chat_id=-1001902595324,
        message_thread_id=392,
        text=f"Оплата пройшла успішно @{await db.get_username(data[1])} {data[1]}\nКод оплати: 1100\nТип: Особиста оплата",
    )
    await message.bot.send_message(
        text=f"Підписка {data[1]} додалась 🟩",
        chat_id=-1001902595324,
        message_thread_id=481,
    )

    # [N] CHECK NEW OR OLD USER AND SEND NOTIFY
    if await db.get_bought_premium(data[1]) > 1:
        expiration_date = await db.get_expiration_date(data[1])
        await message.bot.send_message(
            chat_id=data[1],
            text=f"Дякую за підписку, її продовження до {expiration_date}",
            reply_markup=hide_kb(),
        )
        return
    expiration_date = await db.get_expiration_date(data[1])
    await message.bot.send_message(
        chat_id=data[1],
        text=f"Дякую за підписку, вона діятиме до {expiration_date}",
        reply_markup=hide_kb(),
    )


@router.message(F.text == "Всі Користувачі 👥")
async def all_people_from_db(message: Message):
    if message.from_user.id not in ADMINS:
        return
    await message.delete()

    db = await Database.setup()
    all_users = await db.get_all_user()
    text = "Всі Користувачі 👥"
    for telegram_id, first_name, username, parsing_post, date_join in all_users:
        date_join = datetime.strptime(date_join, "%Y-%m-%d %H:%M:%S.%f")
        formatted_date = date_join.strftime("%Y-%m-%d %H:%M")
        text += f"\nID: {telegram_id}"
        text += f"\nІм`я: {first_name}"
        text += f"\nПсевдонім: {username}"
        text += f"\nСтворив постів: {parsing_post}"
        text += f"\nПриєднався: {formatted_date}\n\n"

    file = types.BufferedInputFile(file=text.encode(), filename=f"Всі Користувачі.txt")
    await message.answer_document(file)


@router.message(F.text == "Всі Користувачі 👑")
async def all_premium_from_db(message: Message):
    if message.from_user.id not in ADMINS:
        return
    await message.delete()

    db = await Database.setup()
    all_premium = await db.get_all_premium()
    text = "Всі користувачі 👑"
    for (
        telegram_id,
        is_premium,
        expiration_date,
        bought_premium,
        date_purchase,
    ) in all_premium:
        text += f"\nID: {telegram_id}"
        text += f"\nПреміум: {'активний' if is_premium else 'не активний'}"
        text += f"\nПокупок: {bought_premium}"
        text += f"\nКупив\\Продовжив: {date_purchase}"
        text += f"\nДіє до: {expiration_date}\n\n"

    file = types.BufferedInputFile(
        file=text.encode(), filename=f"Користувачі що купували.txt"
    )
    await message.answer_document(file)


@router.message(F.text == "Користувачі що не мали 👑")
async def people_ex(message: Message):
    if message.from_user.id not in ADMINS:
        return
    await message.delete()

    db = await Database.setup()
    all_users = await db.get_all_user()
    premium_users = await db.get_all_premium_telegram_id()
    premium_users = [item[0] for item in premium_users]
    new = "Користувачі, що не купували 👑:"

    for telegram_id, _, username, parsing_post, date_join in all_users:
        if telegram_id not in premium_users:
            date_join = datetime.strptime(date_join, "%Y-%m-%d %H:%M:%S.%f")
            formatted_date = date_join.strftime("%Y-%m-%d %H:%M")
            new += f"\nІм`я: @{username}\nID: {telegram_id}\nВикористав тест: {'так' if parsing_post > 0 else 'ні'}\nПриєднався: {formatted_date}\n"

    file = types.BufferedInputFile(
        file=new.encode(), filename=f"Не купували преміум.txt"
    )
    await message.answer_document(file)


@router.message(F.text == "Статистика 📊")
async def stats(message: Message):
    await message.delete()
    if message.from_user.id not in ADMINS:
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
        f"Зароблено гривень - {stats_1day['sum'] if stats_1day['sum'] else zero}\n\n"
        f"Тиждень:\n"
        f"К-ть покупок - {stats_7day['count']}\n"
        f"Зароблено гривень - {stats_7day['sum'] if stats_7day['sum'] else zero}\n\n"
        f"Місяць:\n"
        f"К-ть покупок - {stats_30day['count']}\n"
        f"Зароблено гривень - {stats_30day['sum'] if stats_30day['sum'] else zero}\n\n"
        f"За весь час:\n"
        f"К-ть покупок - {stats_all_time['count']}\n"
        f"Зароблено гривень - {stats_all_time['sum'] if stats_all_time['sum'] else zero}\n\n"
    )

    await message.answer(text=generated_message, reply_markup=hide_kb())


@router.message(F.text == "Розсилка 📢")
async def alarm(message: Message):
    if message.from_user.id not in ADMINS:
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
async def send_news_users(message: Message, state: FSMContext):
    data = await state.get_data()
    message_text = data["message"]
    await state.clear()
    try:
        await message.bot.send_message(
            chat_id=message.text, text=f"Адміністратор бота написав: \n{message_text}"
        )
        await message.answer("Повідомлення надіслано")
    except:
        await message.answer("Користувача не знайдено!")


@router.callback_query(F.data == "Преміум 👑")
async def send_alarm_premium(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await query.message.answer("Напишіть повідомлення: ")
    await state.set_state(SendNews.send_news_premium)


@router.message(SendNews.send_news_premium, F.text)
async def send_news_premium(message: Message, state: FSMContext):
    db = await Database.setup()
    await state.clear()

    premium_user_ids = map(lambda e: e[0], await db.get_all_premium_telegram_id())

    if not premium_user_ids:
        await message.answer("Немає людей з підпискою")
        return

    await asyncio.gather(*map(send_notification(message), premium_user_ids))

    await message.answer("Надсилання закінчено!")


@router.message(SendNews.send_news_users, F.text)
async def send_mixed_news2(message: Message, state: FSMContext):
    db = await Database.setup()
    await state.clear()

    user_ids = map(lambda e: e[0], await db.get_all_user_telegram_id())

    if not user_ids:
        await message.answer("у боті немає людей")
        return

    await asyncio.gather(*map(send_notification(message), user_ids))

    await message.answer("Надсилання закінчено!")


def send_notification(message: Message):
    async def wrapped(user_id: int):
        try:
            await message.bot.send_message(user_id, text=message.text)
        except:
            pass

    return wrapped
