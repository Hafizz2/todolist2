"""Group-chat handlers: registration when the bot is added/removed, /setup, /join."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from html import escape

from aiogram import Bot, F, Router
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.filters import JOIN_TRANSITION, LEAVE_TRANSITION, ChatMemberUpdatedFilter, Command
from aiogram.types import ChatMemberUpdated, Message

from ..config import Settings
from ..i18n import DEFAULT_LANG, t
from ..keyboards import open_app_keyboard, open_settings_keyboard
from ..repo import Repo, User
from ..schedule import local_date
from ..summary import MemberInfo, member_progress, today_text

log = logging.getLogger(__name__)

GROUP_TYPES = {ChatType.GROUP, ChatType.SUPERGROUP}
ADMIN_STATUSES = {ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR}


async def bot_added(event: ChatMemberUpdated, repo: Repo, bot: Bot) -> None:
    await repo.upsert_group(event.chat.id, event.chat.title or "")
    adder = await repo.upsert_user(event.from_user.id, event.from_user.full_name)
    log.info("Bot added to chat %s by %s", event.chat.id, event.from_user.id)
    await bot.send_message(event.chat.id, t(adder.lang, "bot_added"))


async def bot_removed(event: ChatMemberUpdated, repo: Repo) -> None:
    await repo.deactivate_group(event.chat.id)
    log.info("Bot removed from chat %s", event.chat.id)


async def group_migrated(message: Message, repo: Repo) -> None:
    await repo.migrate_group(message.chat.id, message.migrate_to_chat_id)
    log.info("Chat %s migrated to %s", message.chat.id, message.migrate_to_chat_id)


async def cmd_setup(
    message: Message, bot: Bot, repo: Repo, settings: Settings, user: User | None
) -> None:
    if user is None:
        await message.reply(t(DEFAULT_LANG, "anonymous_admin"))
        return

    member = await bot.get_chat_member(message.chat.id, user.telegram_id)
    if member.status not in ADMIN_STATUSES:
        await message.reply(t(user.lang, "setup_not_admin"))
        return

    group = await repo.upsert_group(message.chat.id, message.chat.title or "")
    group = await repo.claim_ownership(group.id, user.id)
    if group.owner_id != user.id:
        owner = await repo.get_user(group.owner_id) if group.owner_id else None
        owner_name = escape(owner.name) if owner else "?"
        await message.reply(t(user.lang, "setup_owned_by_other", owner=owner_name))
        return

    await repo.add_member(group.id, user.id)
    await repo.seed_default_goals(group.id, user.lang)
    me = await bot.me()
    await message.reply(
        t(user.lang, "setup_done", name=escape(user.name)),
        reply_markup=open_settings_keyboard(
            user.lang, me.username, settings.miniapp_short_name, group.id
        ),
    )


async def cmd_join(
    message: Message, bot: Bot, repo: Repo, settings: Settings, user: User | None
) -> None:
    if user is None:
        await message.reply(t(DEFAULT_LANG, "anonymous_join"))
        return

    group = await repo.upsert_group(message.chat.id, message.chat.title or "")
    added = await repo.add_member(group.id, user.id)
    key = "join_done" if added else "join_already"
    me = await bot.me()
    await message.reply(
        t(user.lang, key, name=escape(user.name)),
        reply_markup=open_app_keyboard(user.lang, me.username, settings.miniapp_short_name),
    )


async def cmd_today(
    message: Message, bot: Bot, repo: Repo, settings: Settings, user: User | None
) -> None:
    if user is None:
        await message.reply(t(DEFAULT_LANG, "anonymous_join"))
        return

    group = await repo.upsert_group(message.chat.id, message.chat.title or "")
    if not await repo.is_member(group.id, user.id):
        await message.reply(t(user.lang, "today_not_member"))
        return
    goals = await repo.group_goals(group.id)
    if not goals:
        await message.reply(t(user.lang, "today_no_goals"))
        return

    day = local_date(group.timezone, datetime.now(UTC))
    entries = await repo.entries([user.id], [g.key for g in goals], day)
    member = MemberInfo(user_id=user.id, name=user.name, hide_stats=False)
    progress = member_progress(goals, member, entries)
    me = await bot.me()
    await message.reply(
        today_text(user.lang, user.name, goals, progress),
        reply_markup=open_app_keyboard(user.lang, me.username, settings.miniapp_short_name),
    )


def build_router() -> Router:
    router = Router(name="group")
    router.message.filter(F.chat.type.in_(GROUP_TYPES))
    router.my_chat_member.filter(F.chat.type.in_(GROUP_TYPES))
    router.my_chat_member.register(bot_added, ChatMemberUpdatedFilter(JOIN_TRANSITION))
    router.my_chat_member.register(bot_removed, ChatMemberUpdatedFilter(LEAVE_TRANSITION))
    router.message.register(group_migrated, F.migrate_to_chat_id)
    router.message.register(cmd_setup, Command("setup"))
    router.message.register(cmd_join, Command("join"))
    router.message.register(cmd_today, Command("today"))
    return router
