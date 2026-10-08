from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from .repo import Repo


class UserMiddleware(BaseMiddleware):
    """Upserts the acting Telegram user and passes it to handlers as `user`.

    `user` is None when the sender can't be identified as a person: anonymous group admins
    and messages sent on behalf of a channel (both arrive with `sender_chat` set).
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        repo: Repo = data["repo"]
        tg_user = event.from_user if isinstance(event, (Message, CallbackQuery)) else None
        anonymous = isinstance(event, Message) and event.sender_chat is not None
        if tg_user is None or tg_user.is_bot or anonymous:
            data["user"] = None
        else:
            data["user"] = await repo.upsert_user(tg_user.id, tg_user.full_name)
        return await handler(event, data)
