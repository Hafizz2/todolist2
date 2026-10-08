"""Private-chat handlers: /start and language choice."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import replace
from html import escape

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message

from ..config import Settings
from ..i18n import SUPPORTED_LANGS, t
from ..keyboards import start_keyboard
from ..repo import Repo, User


def _welcome(user: User) -> str:
    return f"{t(user.lang, 'welcome', name=escape(user.name))}\n\n{t(user.lang, 'choose_language')}"


async def cmd_start(message: Message, bot: Bot, settings: Settings, user: User) -> None:
    me = await bot.me()
    await message.answer(
        _welcome(user),
        reply_markup=start_keyboard(user.lang, me.username, settings.miniapp_short_name),
    )


async def cb_set_lang(
    callback: CallbackQuery, bot: Bot, repo: Repo, settings: Settings, user: User | None
) -> None:
    lang = (callback.data or "").removeprefix("lang:")
    if user is None or lang not in SUPPORTED_LANGS:
        await callback.answer()
        return

    await repo.set_user_lang(user.id, lang)
    user = replace(user, lang=lang)
    await callback.answer(t(lang, "language_set"))

    if isinstance(callback.message, Message):
        me = await bot.me()
        # Re-picking the language already shown would be a no-op edit, which Telegram rejects.
        with suppress(TelegramBadRequest):
            await callback.message.edit_text(
                _welcome(user),
                reply_markup=start_keyboard(lang, me.username, settings.miniapp_short_name),
            )


async def cmd_group_only(message: Message, user: User) -> None:
    await message.answer(t(user.lang, "group_only"))


def build_router() -> Router:
    router = Router(name="private")
    router.message.filter(F.chat.type == ChatType.PRIVATE)
    router.message.register(cmd_start, CommandStart())
    router.callback_query.register(cb_set_lang, F.data.startswith("lang:"))
    router.message.register(cmd_group_only, Command("setup", "join"))
    return router
