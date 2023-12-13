from control_db.create_db import BaseDBPart
from datetime import datetime


class PremiumOperations(BaseDBPart):
    async def telegram_id_exists(self, telegram_id):
        result = await (
            await self.cur.execute(
                """SELECT COUNT(`telegram_id`) 
                                            FROM `premium_operations` 
                                            WHERE `telegram_id` = ?""",
                (telegram_id,),
            )
        ).fetchall()
        return bool(result[0][0])

    async def add_operation(self, telegram_id):
        current_datetime = (datetime.now()).strftime("%d.%m.%Y")
        price = 300
        await self.cur.execute(
            """INSERT INTO premium_user(
                                  telegram_id, is_premium, expiration_date,
                                  bought_premium, date_purchase)
                                  VALUES (?,?,?,?,?)
                                  """,
            (
                telegram_id,
                current_datetime,
                price,
            ),
        )
