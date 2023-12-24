from control_db.create_db import BaseDBPart


class PremiumOperations(BaseDBPart):
    async def add_premium_operations(
        self, telegram_id: int, data_operation: str, price: int
    ):
        price = int((str(price))[0:-2])
        await self.cur.execute(
            "INSERT INTO premium_operations (telegram_id, data_operation, price) VALUES(?,?,?)",
            (telegram_id, data_operation, price),
        )

        return await self.base.commit()
