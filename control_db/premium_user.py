from control_db.create_db import BaseDBPart


class PremiumUser(BaseDBPart):
    async def telegram_id_exists(self, telegram_id):
        result = await (await self.cur.execute("""SELECT COUNT(`telegram_id`) 
                                         FROM `premium_user` 
                                         WHERE `telegram_id` = ?""", 
                                         (telegram_id,))).fetchall()
        return bool(result[0][0])
