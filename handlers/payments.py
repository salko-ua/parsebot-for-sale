import dataclasses
import hmac
import random
import string
import typing as t
from datetime import datetime

import aiohttp
from aiogram import F, Router
from aiogram.types import CallbackQuery

from config import MERCHANT_ACCOUNT, MERCHANT_DOMAIN_NAME, SECRET_KEY
from control_db import Database
from keyboards.menu import hide_kb
from keyboards.premium import buy_url
from main import bot

router = Router()


@dataclasses.dataclass
class CreateInvoice:
    invoice_url: str
    reason: str
    reason_code: int

    @classmethod
    def from_dict(cls, dict_: dict) -> t.Self:
        return cls(
            invoice_url=dict_["invoiceUrl"],
            reason=dict_["reason"],
            reason_code=dict_["reasonCode"],
        )


@dataclasses.dataclass
class CheckStatus:
    reason: str
    reason_code: int
    order_reference: str
    amount: int
    currency: str
    transaction_status: str
    merchant_signature: str

    @classmethod
    def from_dict(cls, dict_: dict) -> t.Self:
        return cls(
            reason=dict_["reason"],
            reason_code=dict_["reasonCode"],
            order_reference=dict_["orderReference"],
            amount=dict_["amount"],
            currency=dict_["currency"],
            transaction_status=dict_["transactionStatus"],
            merchant_signature=dict_["merchantSignature"],
        )


@dataclasses.dataclass
class RemoveInvoice:
    reason: str
    reason_code: int

    @classmethod
    def from_dict(cls, dict_: dict) -> t.Self:
        return cls(
            reason=dict_["reason"],
            reason_code=dict_["reasonCode"],
        )


def create_hash(to_encode: list[str | int | None]) -> str:
    to_hash = ""
    for element in to_encode:
        to_hash += (str(element) if element is not None else "") + ";"
    hash = hmac.new(
        SECRET_KEY.encode("utf-8"), to_hash[:-1].encode("utf-8"), "MD5"
    ).hexdigest()
    return hash


def generate_random_string(length: int) -> str:
    return "".join(random.choice(string.ascii_uppercase) for _ in range(length))


async def create_payment(
    order_reference: str,
    order_date: int,
    amount: int,
    currency: str,
    product_name: list,
    product_count: list,
    product_price: list,
) -> CreateInvoice:
    merchant_signature = create_hash(
        [
            MERCHANT_ACCOUNT,
            MERCHANT_DOMAIN_NAME,
            order_reference,
            order_date,
            amount,
            currency,
            *product_name,
            *product_count,
            *product_price,
        ]
    )
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.wayforpay.com/api",
            json={
                "transactionType": "CREATE_INVOICE",
                "merchantAccount": MERCHANT_ACCOUNT,
                "merchantTransactionType": "AUTO",
                "merchantDomainName": MERCHANT_DOMAIN_NAME,
                "merchantSignature": merchant_signature,
                "apiVersion": 1,
                "language": "UA",
                "notifyMethod": "bot",
                "orderReference": order_reference,
                "orderDate": order_date,
                "alternativeAmount": 350,
                "amount": amount,
                "currency": currency,
                "productName": list(product_name),
                "productCount": list(product_count),
                "productPrice": list(product_price),
            },
        ) as response:
            return CreateInvoice.from_dict(await response.json())


async def remove_invoice(order_reference: str, merchant_account: str) -> RemoveInvoice:
    merchant_signature = create_hash([merchant_account, order_reference])
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.wayforpay.com/api",
            json={
                "transactionType": "REMOVE_INVOICE",
                "merchantAccount": merchant_account,
                "orderReference": order_reference,
                "merchantSignature": merchant_signature,
                "apiVersion": "1",
            },
        ) as response:
            return RemoveInvoice.from_dict(await response.json())


async def get_payment_info(order_reference: str, merchant_account: str) -> CheckStatus:
    merchant_signature = create_hash([merchant_account, order_reference])
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.wayforpay.com/api",
            json={
                "transactionType": "CHECK_STATUS",
                "merchantAccount": merchant_account,
                "orderReference": order_reference,
                "merchantSignature": merchant_signature,
                "apiVersion": "1",
            },
        ) as response:
            return CheckStatus.from_dict(await response.json())


@router.callback_query(F.data == "Продовжити підписку 💳")
@router.callback_query(F.data == "Придбати підписку 💳")
async def payment(query: CallbackQuery):
    db = await Database.setup()
    amount = 300
    currency = "UAH"
    product_name = ("Місячна підписка", "Комісія")
    product_count = (int(1), int(1))
    product_price = (int(300), int(0))
    order_reference = generate_random_string(12)
    order_date = int(datetime.now().replace(hour=0, minute=0, second=0).timestamp())

    response = await create_payment(
        order_reference,
        order_date,
        amount,
        currency,
        product_name,
        product_count,
        product_price,
    )

    description = (
        "👑 Підписка на телеграм бота для парсингу\n\n"
        "💸 Тариф: 1 місяць / 300 грн\n\n"
        "🛠 Послуги: Відкриття доступу до парсингу даних с сайту ОЛХ"
    )

    if response.reason_code == 1100:
        await query.message.delete()
        message = await query.message.answer(
            description, reply_markup=buy_url(response.invoice_url, order_reference)
        )

    # Початкові дані
    await db.update_premium_operations(
        telegram_id=query.from_user.id,
        message_id=message.message_id,
        order_date=order_date,
        order_reference=order_reference,
        reason_code=1151,
        transaction_status="Declined",
        price=amount,
    )


async def check_status_invoice(
    response: CheckStatus,
    reference: str,
):
    db = await Database.setup()
    data = (await db.get_order_reference(reference))[0]
    telegram_id = data[0]
    message_id = data[1]

    if response.transaction_status == "Approved":
        # [N] ADD PREMIUM TO USER
        await db.add_premium_user(telegram_id)

        # [N] DELETE OLD MESSAGE
        await bot.delete_message(chat_id=telegram_id, message_id=message_id)

        # [N] UPDATE CODE IN BD
        await db.update_premium_operations(
            reason_code=response.reason_code,
            transaction_status=response.transaction_status,
            order_reference=response.order_reference,
        )

        # [N] NOTIFY ADMINISTARTOR
        await bot.send_message(
            chat_id=-1001902595324,
            message_thread_id=392,
            text=f"Оплата пройшла успішно @{await db.get_username(telegram_id)} {telegram_id}\nКод оплати {response.reason_code}\nКод підписки {reference}",
        )
        await bot.send_message(
            text=f"Підписка {telegram_id} додалась 🟩",
            chat_id=-1001902595324,
            message_thread_id=481,
        )

        # [N] CHECK NEW OR OLD USER AND SEND NOTIFY
        if await db.get_bought_premium(telegram_id) > 1:
            expiration_date = await db.get_expiration_date(telegram_id)
            await bot.send_message(
                chat_id=telegram_id,
                text=f"Дякую за підписку, її продовженно до {expiration_date}",
                reply_markup=hide_kb(),
            )
            return

        expiration_date = await db.get_expiration_date(telegram_id)
        await bot.send_message(
            chat_id=telegram_id,
            text=f"Дякую за підписку, вона діятиме до {expiration_date}",
            reply_markup=hide_kb(),
        )
        return

    if response.transaction_status == "Declined" and response.reason_code != 1151:
        # [N] TRY DELETE OLD MESSAGE
        try:
            await bot.delete_message(chat_id=telegram_id, message_id=message_id)
        except:
            pass

        # [N] UPDATE CODE IN BD
        await db.update_premium_operations(
            reason_code=response.reason_code,
            transaction_status=response.transaction_status,
            order_reference=response.order_reference,
        )

        # [N] NOTIFY ADMINISTARTOR
        await bot.send_message(
            chat_id=-1001902595324,
            message_thread_id=392,
            text=f"Оплата провалилась @{await db.get_username(telegram_id)} {telegram_id}\nКод оплати {response.reason_code}\nКод підписки {reference}",
        )

        # [N] SEND NOTIFY
        await bot.send_message(
            chat_id=telegram_id,
            text=f"Оплату нажаль було відхиленно 😕\nЯкщо є питання за додатковою інформацією зверніться до @realtor_057",
            reply_markup=hide_kb(),
        )
        return


@router.callback_query(F.data.startswith("Передумав ❌"))
async def cancel_invoice(query: CallbackQuery):
    merchant_account = "t_me_48799"
    order_reference = query.data[-12:]
    await query.message.delete()
    await remove_invoice(
        merchant_account=merchant_account, order_reference=order_reference
    )
