from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, CallbackQuery, Message
import aiohttp
from aiogram import F


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
        if (
            isinstance(event, CallbackQuery)
            and event.message
            and event.message.chat.type == "private"
        ):
            return await handler(event, data)
        elif isinstance(event, Message) and event.chat.type == "private":
            return await handler(event, data)
        else:
            await event.delete()
