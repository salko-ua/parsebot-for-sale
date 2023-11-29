from control_db.create_db import BaseDBPart


class UserDB(BaseDBPart):
    async def telegram_id_exists(self, telegram_id):
        result = await (await self.cur.execute("""SELECT COUNT(`telegram_id`) 
                                         FROM `user` 
                                         WHERE `telegram_id` = ?""", 
                                         (telegram_id,))).fetchall()
        return bool(result[0][0])
    
    async def add_user(self, telegram_id, first_name, username, date_join):
        await self.cur.execute("""INSERT INTO user(
                                  telegram_id, first_name,
                                  username, date_join)
                                  VALUES (?,?,?,?)
                               """, 
                               (telegram_id, first_name, username, date_join,))
        
        return await self.base.commit()
