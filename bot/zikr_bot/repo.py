"""Database access for the bot. Plain SQL against the schema in db/*.sql."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

import aiomysql

from .goals import DEFAULT_GOALS
from .i18n import t
from .summary import Entries, GoalInfo, MemberInfo


@dataclass(frozen=True)
class User:
    id: int
    telegram_id: int
    name: str
    lang: str


@dataclass(frozen=True)
class Group:
    id: int
    chat_id: int
    title: str
    owner_id: int | None
    timezone: str
    active: bool


@dataclass(frozen=True)
class ScheduledGroup:
    id: int
    chat_id: int
    title: str
    timezone: str
    morning_time: time
    night_time: time
    privacy_mode: str
    lang: str  # the owner's language, used for the group's posts


def _time(value: timedelta | time) -> time:
    """aiomysql returns TIME columns as timedelta."""
    if isinstance(value, time):
        return value
    return (datetime.min + value).time()


_USER_COLS = "id, telegram_id, name, lang"
_GROUP_COLS = "id, chat_id, title, owner_id, timezone, active"


def _user(row: tuple) -> User:
    return User(id=row[0], telegram_id=row[1], name=row[2], lang=row[3])


def _group(row: tuple) -> Group:
    return Group(
        id=row[0],
        chat_id=row[1],
        title=row[2],
        owner_id=row[3],
        timezone=row[4],
        active=bool(row[5]),
    )


class Repo:
    def __init__(self, pool: aiomysql.Pool) -> None:
        self._pool = pool

    # --- users -----------------------------------------------------------

    async def upsert_user(self, telegram_id: int, name: str) -> User:
        """Create the user on first contact; keep their display name fresh afterwards."""
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO users (telegram_id, name) VALUES (%s, %s) "
                "ON DUPLICATE KEY UPDATE name = VALUES(name)",
                (telegram_id, name[:255]),
            )
            await cur.execute(
                f"SELECT {_USER_COLS} FROM users WHERE telegram_id = %s", (telegram_id,)
            )
            return _user(await cur.fetchone())

    async def get_user(self, user_id: int) -> User | None:
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(f"SELECT {_USER_COLS} FROM users WHERE id = %s", (user_id,))
            row = await cur.fetchone()
            return _user(row) if row else None

    async def set_user_lang(self, user_id: int, lang: str) -> None:
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute("UPDATE users SET lang = %s WHERE id = %s", (lang, user_id))

    # --- groups ----------------------------------------------------------

    async def upsert_group(self, chat_id: int, title: str) -> Group:
        """Register the chat (or re-activate it if the bot was re-added) and refresh its title."""
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO `groups` (chat_id, title) VALUES (%s, %s) "
                "ON DUPLICATE KEY UPDATE title = VALUES(title), active = 1",
                (chat_id, title[:255]),
            )
            await cur.execute(f"SELECT {_GROUP_COLS} FROM `groups` WHERE chat_id = %s", (chat_id,))
            return _group(await cur.fetchone())

    async def get_group(self, group_id: int) -> Group | None:
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(f"SELECT {_GROUP_COLS} FROM `groups` WHERE id = %s", (group_id,))
            row = await cur.fetchone()
            return _group(row) if row else None

    async def deactivate_group(self, chat_id: int) -> None:
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute("UPDATE `groups` SET active = 0 WHERE chat_id = %s", (chat_id,))

    async def migrate_group(self, old_chat_id: int, new_chat_id: int) -> None:
        """A basic group became a supergroup and got a new chat id; keep its data.

        If the new chat id was already auto-registered (an update from the supergroup arrived
        first) and nobody has claimed it yet, that placeholder row is dropped in favour of the
        original group.
        """
        async with self._pool.acquire() as conn:
            await conn.begin()
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "DELETE FROM `groups` WHERE chat_id = %s AND owner_id IS NULL",
                        (new_chat_id,),
                    )
                    await cur.execute("SELECT 1 FROM `groups` WHERE chat_id = %s", (new_chat_id,))
                    if await cur.fetchone() is None:
                        await cur.execute(
                            "UPDATE `groups` SET chat_id = %s WHERE chat_id = %s",
                            (new_chat_id, old_chat_id),
                        )
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise

    async def claim_ownership(self, group_id: int, user_id: int) -> Group:
        """Make `user_id` the owner if the group has none yet. Returns the group afterwards,
        so the caller can compare `owner_id` to see who actually owns it."""
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(
                "UPDATE `groups` SET owner_id = %s WHERE id = %s AND owner_id IS NULL",
                (user_id, group_id),
            )
            await cur.execute(f"SELECT {_GROUP_COLS} FROM `groups` WHERE id = %s", (group_id,))
            return _group(await cur.fetchone())

    # --- membership ------------------------------------------------------

    async def add_member(self, group_id: int, user_id: int) -> bool:
        """Returns True if the user was newly added, False if already a member."""
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(
                "INSERT IGNORE INTO group_members (group_id, user_id) VALUES (%s, %s)",
                (group_id, user_id),
            )
            return cur.rowcount == 1

    # --- goals -----------------------------------------------------------

    async def seed_default_goals(self, group_id: int, lang: str) -> None:
        """Give a group with no goals the starter set. Labels use the owner's language;
        the Mini App shows its own translation for these well-known keys anyway."""
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute("SELECT 1 FROM goals WHERE group_id = %s LIMIT 1", (group_id,))
            if await cur.fetchone() is not None:
                return
            await cur.executemany(
                "INSERT IGNORE INTO goals (group_id, goal_key, label, type, target) "
                "VALUES (%s, %s, %s, %s, %s)",
                [
                    (group_id, g.key, t(lang, f"goal_{g.key}"), g.type, g.target)
                    for g in DEFAULT_GOALS
                ],
            )

    async def group_goals(self, group_id: int) -> list[GoalInfo]:
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(
                "SELECT goal_key, label, type, target FROM goals "
                "WHERE group_id = %s AND active = 1 ORDER BY id",
                (group_id,),
            )
            return [
                GoalInfo(key=r[0], label=r[1], type=r[2], target=r[3]) for r in await cur.fetchall()
            ]

    # --- scheduled posts -------------------------------------------------

    async def schedulable_groups(self) -> list[ScheduledGroup]:
        """Active groups that finished /setup, with their owner's language."""
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(
                "SELECT g.id, g.chat_id, g.title, g.timezone, g.morning_time, g.night_time, "
                "g.privacy_mode, u.lang FROM `groups` g JOIN users u ON u.id = g.owner_id "
                "WHERE g.active = 1"
            )
            return [
                ScheduledGroup(
                    id=r[0],
                    chat_id=r[1],
                    title=r[2],
                    timezone=r[3],
                    morning_time=_time(r[4]),
                    night_time=_time(r[5]),
                    privacy_mode=r[6],
                    lang=r[7],
                )
                for r in await cur.fetchall()
            ]

    async def claim_post(self, group_id: int, kind: str, post_date: date) -> bool:
        """Records the post as sent; False if it already was (so it's never sent twice)."""
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(
                "INSERT IGNORE INTO group_posts (group_id, kind, post_date) VALUES (%s, %s, %s)",
                (group_id, kind, post_date),
            )
            return cur.rowcount == 1

    async def release_post(self, group_id: int, kind: str, post_date: date) -> None:
        """Undo a claim after a failed send, so the next tick retries."""
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(
                "DELETE FROM group_posts WHERE group_id = %s AND kind = %s AND post_date = %s",
                (group_id, kind, post_date),
            )

    # --- progress --------------------------------------------------------

    async def group_members(self, group_id: int) -> list[MemberInfo]:
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(
                "SELECT u.id, u.name, m.hide_my_stats FROM group_members m "
                "JOIN users u ON u.id = m.user_id WHERE m.group_id = %s ORDER BY m.joined_at",
                (group_id,),
            )
            return [
                MemberInfo(user_id=r[0], name=r[1], hide_stats=bool(r[2]))
                for r in await cur.fetchall()
            ]

    async def is_member(self, group_id: int, user_id: int) -> bool:
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(
                "SELECT 1 FROM group_members WHERE group_id = %s AND user_id = %s",
                (group_id, user_id),
            )
            return await cur.fetchone() is not None

    async def entries(self, user_ids: list[int], goal_keys: list[str], entry_date: date) -> Entries:
        if not user_ids or not goal_keys:
            return {}
        users = ", ".join(["%s"] * len(user_ids))
        keys = ", ".join(["%s"] * len(goal_keys))
        async with self._pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(
                f"SELECT user_id, goal_key, amount FROM entries "
                f"WHERE entry_date = %s AND user_id IN ({users}) AND goal_key IN ({keys})",
                (entry_date, *user_ids, *goal_keys),
            )
            return {(r[0], r[1]): r[2] for r in await cur.fetchall()}
