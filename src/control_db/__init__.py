import os

import asyncache
import aiosqlite

from src.control_db.premium_operations import PremiumOperations
from src.control_db.premium_user import PremiumUser
from src.control_db.urls import UrlsDB
from src.control_db.user import UserDB


class Database(UserDB, UrlsDB, PremiumOperations, PremiumUser):
    @classmethod
    @asyncache.cached({})
    async def setup(cls):
        if not os.path.exists("./data"):
            os.mkdir("./data")

        base = await aiosqlite.connect("data/database.db")
        cur = await base.cursor()

        if base:
            print("DATA BASE CONNECTED")


        await base.execute(
            """
            CREATE TABLE IF NOT EXISTS user(
                telegram_id       INTEGER NOT NULL,
                group_id          INTEGER DEFAULT 0,
                first_name        TEXT,     -- ім`я
                username          TEXT,     -- особливе ім`я
                parsing_post      INTEHER DEFAULT 0,
                date_join         TEXT,     -- дата коли перший раз написав бот
                template          TEXT DEFAULT ''
            )
            """
        )
        await base.execute(
            """
            CREATE TABLE IF NOT EXISTS premium_user(
                telegram_id       INTEGER NOT NULL, 
                is_premium        BOOLEAN,  -- чи активна зараз підписка
                expiration_date   INTEGER,    -- дата до якої діє преміум
                bought_premium    INTEGER,    -- к-ть купівель підписки 
                date_purchase     TEXT     -- коли купив підписку яка зараз активна
            )
            """
        )
        await base.execute(
            """
            CREATE TABLE IF NOT EXISTS premium_operations(
                telegram_id       INTEGER NOT NULL,
                message_id        INTEHER NOT NULL,
                order_date        FLOAT NOT NULL,
                order_reference   TEXT NOT NULL,
                reason_code       INTEGER DEFAULT 1151,
                transaction_status TEXT,
                price             INTEGER DEFAULT 300
            )
            """
        )
        await base.execute(
            """
            CREATE TABLE IF NOT EXISTS urls(
                telegram_id       INTEGER NOT NULL, 
                date              FLOAT NOT NULL,
                url               TEXT NOT NULL
            )
            """
        )

        await base.commit()
        return cls(base, cur)
