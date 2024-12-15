from src.database.create_db import BaseDBPart


class UrlsDB(BaseDBPart):
    async def add_url(self, telegram_id: int, url: str, date: float):
        await self.cur.execute(
            "INSERT INTO urls(telegram_id, date, url) VALUES(?,?,?)",
            (
                telegram_id,
                date,
                url,
            ),
        )

        urls = await (
            await self.cur.execute(
                "SELECT COUNT(*) FROM urls WHERE telegram_id = ?", (telegram_id,)
            )
        ).fetchall()

        if urls[0][0] > 5:
            await self.cur.execute(
                """
                DELETE FROM urls WHERE telegram_id = ? AND date NOT IN (
                SELECT date FROM urls WHERE telegram_id = ? ORDER BY date DESC LIMIT 5
                )""",
                (telegram_id, telegram_id),
            )

        await self.base.commit()

    async def see_urls(self, telegram_id):
        urls = await (
            await self.cur.execute(
                "SELECT url FROM urls WHERE telegram_id = ? ORDER BY date DESC",
                (telegram_id,),
            )
        ).fetchall()
        if len(urls) > 5:
            urls = urls[:5]

        return urls
