from datetime import datetime, timedelta
from typing import Iterable

from aiosqlite import Row

from src.control_db.create_db import BaseDBPart


class PremiumOperations(BaseDBPart):
    async def update_premium_operations(
        self,
        order_reference: str,
        reason_code: int,
        transaction_status: str,
        telegram_id: int | None = None,
        message_id: int | None = None,
        order_date: int | None = None,
        price: int = 300,
    ):
        response = await (
            await self.cur.execute(
                "SELECT COUNT(order_reference) FROM premium_operations WHERE order_reference = ?",
                (order_reference,),
            )
        ).fetchall()

        if not response[0][0]:
            await self.cur.execute(
                """INSERT INTO premium_operations 
                    (telegram_id, message_id, order_date, 
                    order_reference, reason_code, transaction_status, price) 
                    VALUES(?,?,?,?,?,?,?)""",
                (
                    telegram_id,
                    message_id,
                    order_date,
                    order_reference,
                    reason_code,
                    transaction_status,
                    price,
                ),
            )
            return await self.base.commit()

        await self.cur.execute(
            "UPDATE premium_operations SET reason_code = ?, transaction_status = ? WHERE order_reference = ?",
            (
                reason_code,
                transaction_status,
                order_reference,
            ),
        )
        return await self.base.commit()

    async def delete_premium_operation(self, telegram_id):
        await self.cur.execute(
            "DELETE FROM premium_operations WHERE telegram_id = ? AND transaction_status = ?",
            (telegram_id, "Approved"),
        )
        await self.base.commit()

    async def check_all_order_reference(self) -> Iterable[Row]:
        return await (
            await self.cur.execute(
                "SELECT order_reference FROM premium_operations WHERE transaction_status IN (?,?) OR reason_code = ?",
                (
                    *["InProcessing", "Pending"],
                    1151,
                ),
            )
        ).fetchall()

    async def get_order_reference(self, order_reference):
        return await (
            await self.cur.execute(
                "SELECT * FROM premium_operations WHERE order_reference = ?",
                (order_reference,),
            )
        ).fetchall()

    async def get_stats_from_operation(self, day: int = None):
        now = datetime.now()
        request = (
            "SELECT COUNT(order_reference), SUM(price) "
            "FROM premium_operations "
            "WHERE order_date >= ? AND order_date <= ? AND transaction_status = ?"
        )

        if day:
            # Отримання операцій
            days = timedelta(days=day)
            start = int((now - days).replace(hour=0, minute=0, second=0).timestamp())
            today = int(now.replace(hour=0, minute=0, second=0).timestamp())
            operations = await (
                await self.cur.execute(request, (start, today, "Approved"))
            ).fetchone()
            return operations

        # Отримання всіх операцій
        all_operations = await (
            await self.cur.execute(
                "SELECT COUNT(order_reference), SUM(price) FROM premium_operations WHERE transaction_status = ?",
                ("Approved",),
            )
        ).fetchone()
        return all_operations
