from src.database.create_db import BaseDBPart


class UserDB(BaseDBPart):
    async def telegram_id_exists(self, telegram_id):
        result = await (
            await self.cur.execute(
                """SELECT COUNT(`telegram_id`) 
                    FROM `user` 
                    WHERE `telegram_id` = ?""",
                (telegram_id,),
            )
        ).fetchall()
        return bool(result[0][0])

    async def get_username(self, telegram_id):
        result = await (
            await self.cur.execute(
                """SELECT username
                    FROM `user` 
                    WHERE `telegram_id` = ?""",
                (telegram_id,),
            )
        ).fetchall()
        return result[0][0]

    async def get_count_users(self):
        result = await (
            await self.cur.execute("SELECT COUNT(`telegram_id`) FROM `user`")
        ).fetchall()
        return result[0][0]

    async def get_all_user_telegram_id(self):
        result = await (
            await self.cur.execute("SELECT telegram_id FROM user")
        ).fetchall()
        return result

    async def get_all_user(self):
        result = await (await self.cur.execute("SELECT * FROM user")).fetchall()
        return result

    async def add_user(self, telegram_id, first_name, username, date_join):
        await self.cur.execute(
            """INSERT INTO user(telegram_id, first_name, username, date_join) VALUES (?,?,?,?)""",
            (
                telegram_id,
                first_name,
                username,
                date_join,
            ),
        )

        return await self.base.commit()

    async def update_count_parsing_post(self, telegram_id):
        await self.cur.execute(
            f"UPDATE user SET parsing_post = parsing_post + ? WHERE telegram_id = ?",
            (1, telegram_id),
        )
        await self.base.commit()

    async def check_count_parsing_post(self, telegram_id):
        return await (
            await self.cur.execute(
                "SELECT parsing_post FROM user WHERE telegram_id = ?", (telegram_id,)
            )
        ).fetchall()
