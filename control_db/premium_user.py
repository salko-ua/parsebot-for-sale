from datetime import datetime
from typing import Iterable

from aiosqlite import Row
from dateutil.relativedelta import relativedelta
from control_db import Database
from control_db.create_db import BaseDBPart


class PremiumUser(BaseDBPart):
    async def telegram_id_premium_exists(self, telegram_id):
        result = await (
            await self.cur.execute(
                """SELECT COUNT(`telegram_id`) FROM `premium_user` WHERE `telegram_id` = ?""",
                (telegram_id,),
            )
        ).fetchall()
        return bool(result[0][0])

    async def turn_premium_user(self, telegram_id: int, turn: int):
        await self.cur.execute(
            "UPDATE premium_user SET is_premium = ? WHERE telegram_id = ?",
            (
                turn,
                telegram_id,
            ),
        )
        return await self.base.commit()

    async def get_count_premium_user(self, is_premium: int):
        result = await (
            await self.cur.execute(
                """SELECT COUNT(`telegram_id`) FROM `premium_user` WHERE is_premium = ?""",
                (is_premium,),
            )
        ).fetchall()
        return result[0][0]

    async def get_all_premium_telegram_id(self):
        result = await (await self.cur.execute("SELECT `telegram_id` FROM premium_user")).fetchall()
        return result

    async def get_all_premium(self):
        result = await (await self.cur.execute("SELECT * FROM premium_user")).fetchall()
        return result

    async def is_premium_user(self, telegram_id):
        result = await (
            await self.cur.execute(
                """SELECT COUNT(`telegram_id`) FROM `premium_user` WHERE `telegram_id` = ? AND `is_premium` = ?""",
                (telegram_id, 1),
            )
        ).fetchall()
        return bool(result[0][0])

    async def get_expiration_date(self, telegram_id):
        expiration_date = await (
            await self.cur.execute(
                """SELECT expiration_date FROM `premium_user` WHERE telegram_id = ?""",
                (telegram_id,),
            )
        ).fetchall()

        return expiration_date[0][0]

    async def get_bought_premium(self, telegram_id):
        bought_premium = await (
            await self.cur.execute(
                """SELECT bought_premium FROM `premium_user` WHERE telegram_id = ?""",
                (telegram_id,),
            )
        ).fetchall()

        return bought_premium[0][0]

    async def get_date_purchase(self, telegram_id):
        date_purchase = await (
            await self.cur.execute(
                """SELECT date_purchase FROM `premium_user` WHERE telegram_id = ?""",
                (telegram_id,),
            )
        ).fetchall()

        return date_purchase[0][0]

    async def delete_premium_user(self, telegram_id):
        await self.cur.execute("DELETE FROM premium_user WHERE telegram_id = ?", (telegram_id,))
        await self.base.commit()

    async def add_premium_user(self, telegram_id):
        db = await Database.setup()
        telegram_id_exists = await (
            await self.cur.execute(
                """SELECT COUNT(`telegram_id`) FROM `premium_user` WHERE telegram_id = ?""",
                (telegram_id,),
            )
        ).fetchall()

        bought_premium = await (
            await self.cur.execute(
                """SELECT bought_premium FROM `premium_user` WHERE telegram_id = ?""",
                (telegram_id,),
            )
        ).fetchall()

        expiration_date = await (
            await self.cur.execute(
                """SELECT expiration_date FROM `premium_user` WHERE telegram_id = ?""",
                (telegram_id,),
            )
        ).fetchall()

        # VARIABLES
        current_datetime = (datetime.now()).strftime("%d.%m.%Y")
        next_month = (datetime.now() + relativedelta(months=1)).strftime("%d.%m.%Y")

        if not bool(telegram_id_exists[0][0]):
            await self.cur.execute(
                """INSERT INTO premium_user(telegram_id, is_premium, expiration_date, bought_premium, date_purchase) 
                VALUES (?,?,?,?,?)""",
                (telegram_id, 1, next_month, 1, current_datetime),
            )
            return await self.base.commit()

        if await db.is_premium_user(telegram_id):
            continue_data = (
                    datetime.strptime(expiration_date[0][0], "%d.%m.%Y") + relativedelta(months=1)
            ).strftime("%d.%m.%Y")
        else:
            continue_data = (datetime.now() + relativedelta(months=1)).strftime("%d.%m.%Y")

        await self.cur.execute(
            """UPDATE premium_user SET is_premium = ?, expiration_date = ?, bought_premium = ?, date_purchase = ? 
            WHERE telegram_id = ?; """,
            (1, continue_data, (bought_premium[0][0] + 1), current_datetime, telegram_id),
        )
        return await self.base.commit()

    async def get_all_premium_user(self) -> Iterable[Row]:
        cursor = await self.cur.execute(
            "SELECT telegram_id, expiration_date FROM premium_user WHERE is_premium = ?",
            (1,),
        )
        rows = await cursor.fetchall()

        return rows
