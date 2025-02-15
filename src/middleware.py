from typing import Any, Awaitable, Callable, Dict

import aiohttp
from aiogram import BaseMiddleware, F
from aiogram.types import CallbackQuery, Message, TelegramObject


class CheckConnectioError(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except aiohttp.ClientConnectionError as e:
            print(f"Error: {e}")


class CheckPrivateChat(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, CallbackQuery):
            assert event.message is not None
            if event.message.chat.type == "private":
                return await handler(event, data)
        elif isinstance(event, Message):
            if event.chat.type == "private":
                return await handler(event, data)

