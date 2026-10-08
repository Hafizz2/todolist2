"""Private-chat handlers: /start, language choice, and the settings deep link."""

from __future__ import annotations

from contextlib import suppress
from dataclasses import replace
from html import escape

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message

from ..config import Settings
from ..i18n import SUPPORTED_LANGS, t
from ..keyboards import parse_setup_payload, settings_webapp_keyboard, start_keyboard
from ..repo import Repo, User


def _welcome(user: User) -> str:
    return f"{t(user.lang, 'welcome', name=escape(user.name))}\n\n{t(user.lang, 'choose_language')}"


async def cmd_start(
    message: Message, command: CommandObject, bot: Bot, repo: Repo, settings: Settings, user: User
) -> None:
    group_id = parse_setup_payload(command.args)
    if group_id is not None:
        await _send_group_settings(message, repo, settings, user, group_id)
        return

    me = await bot.me()
    await message.answer(_welcome(user), reply_markup=start_keyboard(user.lang, me.username))


async def _send_group_settings(
    message: Message, repo: Repo, settings: Settings, user: User, group_id: int
) -> None:
    group = await repo.get_group(group_id)
    if group is None or not group.active:
        await message.answer(t(user.lang, "group_not_found"))
        return
    if group.owner_id != user.id:
        await message.answer(t(user.lang, "settings_not_owner"))
        return
    await message.answer(
        t(user.lang, "settings_intro", title=escape(group.title)),
        reply_markup=settings_webapp_keyboard(user.lang, settings.miniapp_url, group.id),
    )


async def cb_set_lang(callback: CallbackQuery, bot: Bot, repo: Repo, user: User | None) -> None:
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
                _welcome(user), reply_markup=start_keyboard(lang, me.username)
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
