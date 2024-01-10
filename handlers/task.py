import asyncio
from datetime import datetime, timedelta
from main import bot

import aiohttp

from config import MERCHANT_ACCOUNT
from control_db import Database
from handlers.payments import check_status_invoice, get_payment_info
from main import scheduler


async def check_all_invoice(lock):
    async with lock:
        db = await Database.setup()
        order_reference = await db.check_all_order_reference()
        print(order_reference, ": list order reference")
        if order_reference != []:
            for reference in order_reference:
                try:
                    response = await get_payment_info(reference[0], MERCHANT_ACCOUNT)
                    print(
                        f"\nREQUEST TO WAYFORPAY\nDATA: \n{reference[0]}\n{response.reason_code}\n{response.transaction_status}"
                    )
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

        print(subscription_dict)

        current_date = datetime.now().date()
        for telegram_id, expiration_date in subscription_dict.items():
            expiration_date_in_3_days = expiration_date - timedelta(days=3)
            if expiration_date_in_3_days == current_date:
                print(f"Підписка для telegram_id {telegram_id} лишилось 3 дні")
            elif expiration_date == current_date:
                print(f"Підписка для telegram_id {telegram_id} лишилось цей день")
            elif expiration_date >= current_date:
                # await bot.send_message(text=f"", chat_id=-1001902595324 message_thread_id=)  # notify admin
                await bot.send_message()  # notify user


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
