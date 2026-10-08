"""Scheduled morning/night posts. One job runs every minute and posts whatever is due in each
group's own timezone, so changing a group's times needs no rescheduling."""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import Settings
from .keyboards import open_app_keyboard
from .repo import Repo, ScheduledGroup
from .schedule import due_posts
from .summary import GoalInfo, morning_text, night_text

log = logging.getLogger(__name__)


async def tick(bot: Bot, repo: Repo, settings: Settings, now: datetime | None = None) -> None:
    now = now or datetime.now(UTC)
    for group in await repo.schedulable_groups():
        for kind, day in due_posts(group.timezone, group.morning_time, group.night_time, now):
            goals = await repo.group_goals(group.id)
            if not goals or not await repo.claim_post(group.id, kind, day):
                continue
            try:
                await _send(bot, repo, settings, group, kind, day, goals)
            except TelegramForbiddenError:
                log.info("Bot can no longer post in chat %s; deactivating", group.chat_id)
                await repo.deactivate_group(group.chat_id)
            except Exception:
                log.exception("Failed to send %s post to chat %s", kind, group.chat_id)
                await repo.release_post(group.id, kind, day)


async def _send(
    bot: Bot,
    repo: Repo,
    settings: Settings,
    group: ScheduledGroup,
    kind: str,
    day: date,
    goals: list[GoalInfo],
) -> None:
    if kind == "morning":
        text = morning_text(group.lang, group.title, goals)
    else:
        members = await repo.group_members(group.id)
        entries = await repo.entries([m.user_id for m in members], [g.key for g in goals], day)
        text = night_text(group.lang, group.title, group.privacy_mode, goals, members, entries)
    me = await bot.me()
    await bot.send_message(
        group.chat_id,
        text,
        reply_markup=open_app_keyboard(group.lang, me.username, settings.miniapp_short_name),
    )


def create_scheduler(bot: Bot, repo: Repo, settings: Settings) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=UTC)
    scheduler.add_job(
        tick,
        CronTrigger(second=0, timezone=UTC),
        kwargs={"bot": bot, "repo": repo, "settings": settings},
        id="minute_tick",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=50,
    )
    return scheduler
