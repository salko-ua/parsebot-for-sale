import asyncio
from datetime import datetime, timedelta

import aiohttp

from src.config import MERCHANT_ACCOUNT
from src.control_db import Database
from src.handlers.payments import check_status_invoice, get_payment_info
from src.keyboards.premium import buy_premium_kb
from src.global_variable import bot, scheduler


async def check_all_invoice(lock):
    async with lock:
        db = await Database.setup()
        order_reference = await db.check_all_order_reference()
        if order_reference:
            for reference in order_reference:
                try:
                    response = await get_payment_info(reference[0], MERCHANT_ACCOUNT)
                    await db.update_premium_operations(
                        order_reference=reference[0],
                        reason_code=response.reason_code,
                        transaction_status=response.transaction_status,
                    )
                    await check_status_invoice(response, reference[0])
                except aiohttp.ClientConnectionError:
                    print("Waiting for the connection")


async def check_all_premium(lock):
    async with lock:
        db = await Database.setup()
        rows = await db.get_all_premium_user()

        subscription_dict = {}

        for row in rows:
            telegram_id, expiration_date_str = row
            expiration_date = datetime.strptime(expiration_date_str, "%d.%m.%Y").date()
            subscription_dict[telegram_id] = expiration_date

        current_date = datetime.now().date()
        for telegram_id, expiration_date in subscription_dict.items():
            text_user = ""
            expiration_date_in_3_days = expiration_date - timedelta(days=3)
            if expiration_date_in_3_days == current_date:
                text_admin = f"Підписка {telegram_id} залишилось 3 дні 🟨"
                text_user = (
                    f"Термін дії вашої підписки закінчиться через 3 дні\n"
                    f"Бажаєте продовжити її?"
                )
            elif expiration_date == current_date:
                text_admin = f"Підписка {telegram_id} останній день 🟧"
                text_user = (
                    f"Термін дії вашої підписки закінчиться завтра\n"
                    "Бажаєте продовжити її?"
                )
            elif expiration_date <= current_date:
                text_admin = f"Підписка {telegram_id} закінчилась 🟥"
                text_user = (
                    f"Термін дії вашої підписки закінчився {expiration_date}\n"
                    "Бажаєте продовжити її?"
                )
                await db.turn_premium_user(telegram_id, 0)

            if text_user:
                await notify_status_premium(
                    text_user=text_user,
                    text_admin=text_admin,
                    telegram_id=telegram_id,
                )


async def notify_status_premium(
    text_user: str, text_admin: str, telegram_id: int
) -> None:
    try:
        await bot.send_message(
            text=text_admin, chat_id=-1001902595324, message_thread_id=481
        )
        await bot.send_message(
            text=text_user, chat_id=telegram_id, reply_markup=buy_premium_kb(True)
        )
    except Exception as e:
        print(f"NOTIFY BLOCK ERROR: {e}")


async def create_tasks():
    if not scheduler.running:
        scheduler.start()
    lock = asyncio.Lock()
    scheduler.add_job(
        check_all_invoice, "interval", seconds=10, id="check_all_invoice", args=(lock,)
    )
    scheduler.add_job(
        check_all_premium, "cron", hour=7, id="check_all_premium", args=(lock,)
    )
