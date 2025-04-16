from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

from src.config import settings


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            telegram_id = event.from_user.id
            if int(telegram_id) == settings.ALLOWED_TG_ID:
                return await handler(event, data)
            else:
                await event.answer("Access denied. Your ID is not authorized.")
        return
