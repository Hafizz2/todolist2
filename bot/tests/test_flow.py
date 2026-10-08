"""End-to-end handler tests: real MySQL (schema from db/*.sql), fake Telegram API.

Skipped unless TEST_DB_HOST is set. The DB user needs CREATE/DROP DATABASE rights, e.g. with
docker-compose running:

    TEST_DB_HOST=127.0.0.1 TEST_DB_USER=root TEST_DB_PASS=root pytest
"""

from __future__ import annotations

import asyncio
import itertools
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import aiomysql
import pytest
from aiogram import Bot, Dispatcher
from aiogram.client.session.base import BaseSession
from aiogram.exceptions import TelegramForbiddenError
from aiogram.methods import (
    AnswerCallbackQuery,
    EditMessageText,
    GetChatMember,
    GetMe,
    SendMessage,
    TelegramMethod,
)
from aiogram.types import (
    CallbackQuery,
    Chat,
    ChatMemberLeft,
    ChatMemberMember,
    ChatMemberOwner,
    ChatMemberUpdated,
    Message,
    Update,
)
from aiogram.types import User as TgUser

from zikr_bot.config import Settings
from zikr_bot.handlers import build_router
from zikr_bot.jobs import tick
from zikr_bot.middlewares import UserMiddleware
from zikr_bot.repo import Repo

DB_HOST = os.environ.get("TEST_DB_HOST")
pytestmark = pytest.mark.skipif(not DB_HOST, reason="TEST_DB_HOST not set")

DB_NAME = "zikr_circle_test"
SQL_DIR = Path(__file__).resolve().parents[2] / "db"
BOT_USER = TgUser(id=999, is_bot=True, first_name="Zikr", username="zikr_test_bot")
GROUP = Chat(id=-1001, type="supergroup", title="Masjid Friends")
ALICE = TgUser(id=101, is_bot=False, first_name="Alice")
BOB = TgUser(id=102, is_bot=False, first_name="Bob")
_ids = itertools.count(1)


def _conn_kwargs() -> dict[str, Any]:
    return {
        "host": DB_HOST,
        "port": int(os.environ.get("TEST_DB_PORT", "3306")),
        "user": os.environ.get("TEST_DB_USER", "root"),
        "password": os.environ.get("TEST_DB_PASS", ""),
        "charset": "utf8mb4",
        "autocommit": True,
    }


async def _reset_database() -> None:
    conn = await aiomysql.connect(**_conn_kwargs())
    async with conn.cursor() as cur:
        await cur.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
        await cur.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4")
        await cur.execute(f"USE {DB_NAME}")
        for path in sorted(SQL_DIR.glob("*.sql")):
            for statement in path.read_text("utf-8").split(";"):
                body = "\n".join(
                    line for line in statement.splitlines() if not line.strip().startswith("--")
                ).strip()
                if body:
                    await cur.execute(body)
    conn.close()


class FakeSession(BaseSession):
    """Answers Bot API calls locally and records them."""

    def __init__(self, admins: set[int]) -> None:
        super().__init__()
        self.admins = admins
        self.calls: list[TelegramMethod[Any]] = []
        self.forbidden_chats: set[int] = set()

    async def make_request(self, bot: Bot, method: TelegramMethod[Any], timeout: int | None = None):
        self.calls.append(method)
        if isinstance(method, GetMe):
            return BOT_USER
        if isinstance(method, GetChatMember):
            user = TgUser(id=method.user_id, is_bot=False, first_name="x")
            if method.user_id in self.admins:
                return ChatMemberOwner(user=user, is_anonymous=False)
            return ChatMemberMember(user=user)
        if isinstance(method, SendMessage):
            if method.chat_id in self.forbidden_chats:
                raise TelegramForbiddenError(method, "Forbidden: bot was kicked from the group")
            return Message(
                message_id=next(_ids),
                date=datetime.now(),
                chat=Chat(id=method.chat_id, type="private"),
                text=method.text,
            )
        if isinstance(method, (AnswerCallbackQuery, EditMessageText)):
            return True
        raise AssertionError(f"unexpected API call {type(method).__name__}")

    async def close(self) -> None:
        pass

    async def stream_content(self, *args: Any, **kwargs: Any):  # pragma: no cover
        raise NotImplementedError
        yield b""

    def texts(self) -> list[str]:
        return [c.text for c in self.calls if isinstance(c, (SendMessage, EditMessageText))]

    def last(self) -> SendMessage:
        return [c for c in self.calls if isinstance(c, SendMessage)][-1]


def _message(chat: Chat, user: TgUser, text: str, **extra: Any) -> Update:
    msg = Message(
        message_id=next(_ids), date=datetime.now(), chat=chat, from_user=user, text=text, **extra
    )
    return Update(update_id=next(_ids), message=msg)


def _private(user: TgUser) -> Chat:
    return Chat(id=user.id, type="private")


class Harness:
    def __init__(self, pool: aiomysql.Pool, admins: set[int]) -> None:
        self.pool = pool
        self.session = FakeSession(admins)
        self.bot = Bot("42:TEST", session=self.session)
        self.settings = Settings(
            "42:TEST", "", 0, DB_NAME, "", "", "https://app.test/miniapp/", "app"
        )
        self.repo = Repo(pool)
        self.dp = Dispatcher(repo=self.repo, settings=self.settings)
        self.dp.message.middleware(UserMiddleware())
        self.dp.callback_query.middleware(UserMiddleware())
        self.dp.include_router(build_router())

    async def feed(self, update: Update) -> None:
        await self.dp.feed_update(self.bot, update)

    async def bot_added(self, by: TgUser) -> None:
        event = ChatMemberUpdated(
            chat=GROUP,
            from_user=by,
            date=datetime.now(),
            old_chat_member=ChatMemberLeft(user=BOT_USER),
            new_chat_member=ChatMemberMember(user=BOT_USER),
        )
        await self.feed(Update(update_id=next(_ids), my_chat_member=event))

    async def tick(self, now: datetime) -> None:
        await tick(self.bot, self.repo, self.settings, now)

    async def execute(self, sql: str, *args: Any) -> None:
        async with self.pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(sql, args)

    async def fetch(self, sql: str, *args: Any) -> list[tuple]:
        async with self.pool.acquire() as conn, conn.cursor() as cur:
            await cur.execute(sql, args)
            return list(await cur.fetchall())


def run(scenario, admins: set[int] = frozenset({ALICE.id})) -> None:
    async def wrapper() -> None:
        await _reset_database()
        pool = await aiomysql.create_pool(db=DB_NAME, **_conn_kwargs())
        try:
            await scenario(Harness(pool, set(admins)))
        finally:
            pool.close()
            await pool.wait_closed()

    asyncio.run(wrapper())


def test_start_registers_user_and_switches_language():
    async def scenario(h: Harness) -> None:
        await h.feed(_message(_private(ALICE), ALICE, "/start"))
        assert await h.fetch("SELECT telegram_id, name, lang FROM users") == [(101, "Alice", "am")]
        markup = h.session.last().reply_markup
        assert markup.inline_keyboard[1][0].url == "https://t.me/zikr_test_bot/app"
        assert "startgroup" in markup.inline_keyboard[2][0].url

        callback = CallbackQuery(
            id="1",
            from_user=ALICE,
            chat_instance="x",
            data="lang:en",
            message=Message(message_id=1, date=datetime.now(), chat=_private(ALICE), text="old"),
        )
        await h.feed(Update(update_id=next(_ids), callback_query=callback))
        assert await h.fetch("SELECT lang FROM users") == [("en",)]
        assert "Assalamu alaikum, Alice" in h.session.texts()[-1]

    run(scenario)


def test_adding_bot_registers_group_and_setup_claims_ownership():
    async def scenario(h: Harness) -> None:
        await h.bot_added(by=ALICE)
        assert await h.fetch("SELECT chat_id, title, owner_id, active FROM `groups`") == [
            (-1001, "Masjid Friends", None, 1)
        ]

        # Non-admin can't run /setup.
        await h.feed(_message(GROUP, BOB, "/setup"))
        assert await h.fetch("SELECT owner_id FROM `groups`") == [(None,)]

        await h.feed(_message(GROUP, ALICE, "/setup"))
        (alice_id,) = (await h.fetch("SELECT id FROM users WHERE telegram_id = 101"))[0]
        (group_id,) = (await h.fetch("SELECT id FROM `groups`"))[0]
        assert await h.fetch("SELECT owner_id FROM `groups`") == [(alice_id,)]
        assert await h.fetch("SELECT user_id FROM group_members") == [(alice_id,)]
        button = h.session.last().reply_markup.inline_keyboard[0][0]
        assert button.url == f"https://t.me/zikr_test_bot/app?startapp=group_{group_id}"

        # First /setup seeds the starter goals, labelled in the owner's language.
        goals = await h.fetch("SELECT goal_key, label, type, target FROM goals ORDER BY id")
        assert len(goals) == 8
        assert ("istighfar", "ኢስቲግፋር", "counter", 100) in goals

        # Running /setup again doesn't duplicate them.
        await h.feed(_message(GROUP, ALICE, "/setup"))
        assert await h.fetch("SELECT COUNT(*) FROM goals") == [(8,)]

    run(scenario)


def test_second_admin_cannot_take_over_ownership():
    async def scenario(h: Harness) -> None:
        await h.feed(_message(GROUP, ALICE, "/setup"))
        await h.feed(_message(GROUP, BOB, "/setup"))
        owners = await h.fetch(
            "SELECT u.telegram_id FROM `groups` g JOIN users u ON u.id = g.owner_id"
        )
        assert owners == [(101,)]
        assert "Alice" in h.session.last().text

    run(scenario, admins={ALICE.id, BOB.id})


def test_join_is_idempotent():
    async def scenario(h: Harness) -> None:
        await h.feed(_message(GROUP, BOB, "/join"))
        await h.feed(_message(GROUP, BOB, "/join"))
        rows = await h.fetch(
            "SELECT u.telegram_id FROM group_members m JOIN users u ON u.id = m.user_id"
        )
        assert rows == [(102,)]
        first, second = h.session.texts()[-2:]
        assert first != second
        assert h.session.last().reply_markup.inline_keyboard[0][0].url == (
            "https://t.me/zikr_test_bot/app"
        )

    run(scenario)


def test_anonymous_admin_is_asked_to_identify():
    async def scenario(h: Harness) -> None:
        anon = TgUser(id=1087968824, is_bot=True, first_name="Group")
        await h.feed(_message(GROUP, anon, "/setup", sender_chat=GROUP))
        assert await h.fetch("SELECT COUNT(*) FROM users") == [(0,)]
        assert await h.fetch("SELECT owner_id FROM `groups`") == []

    run(scenario)


def test_removal_and_migration_keep_group_data():
    async def scenario(h: Harness) -> None:
        old = Chat(id=-55, type="group", title="Small")
        await h.feed(_message(old, ALICE, "/setup"))
        # A placeholder row for the new supergroup id appeared before the migration message.
        await h.feed(_message(Chat(id=-1009, type="supergroup", title="Small"), BOB, "/join"))
        await h.feed(_message(old, ALICE, "", migrate_to_chat_id=-1009))
        rows = await h.fetch("SELECT chat_id, owner_id IS NOT NULL FROM `groups`")
        assert rows == [(-1009, 1)]

        event = ChatMemberUpdated(
            chat=Chat(id=-1009, type="supergroup", title="Small"),
            from_user=ALICE,
            date=datetime.now(),
            old_chat_member=ChatMemberMember(user=BOT_USER),
            new_chat_member=ChatMemberLeft(user=BOT_USER),
        )
        await h.feed(Update(update_id=next(_ids), my_chat_member=event))
        assert await h.fetch("SELECT active FROM `groups`") == [(0,)]

    run(scenario)


# 06:00 / 21:00 in Africa/Addis_Ababa (UTC+3) on 2026-10-09.
MORNING_UTC = datetime(2026, 10, 9, 3, 0, tzinfo=UTC)
NIGHT_UTC = datetime(2026, 10, 9, 18, 0, tzinfo=UTC)


async def _set_up_group_with_members(h: Harness) -> None:
    await h.feed(_message(GROUP, ALICE, "/setup"))  # Alice owns it; starter goals seeded
    await h.feed(_message(GROUP, BOB, "/join"))
    await h.execute("UPDATE users SET lang = 'en'")  # posts use the owner's language


def test_morning_and_night_posts_are_sent_once():
    async def scenario(h: Harness) -> None:
        await _set_up_group_with_members(h)
        (bob_id,) = (await h.fetch("SELECT id FROM users WHERE telegram_id = 102"))[0]
        for key in ("salat_fajr", "salat_dhuhr"):
            await h.execute(
                "INSERT INTO entries (user_id, goal_key, entry_date, amount) "
                "VALUES (%s, %s, '2026-10-09', 1)",
                bob_id,
                key,
            )

        sent_before = len(h.session.texts())
        await h.tick(MORNING_UTC)
        await h.tick(MORNING_UTC.replace(minute=1))  # next minute: already sent
        posts = h.session.texts()[sent_before:]
        assert len(posts) == 1
        assert "Today's challenge" in posts[0] and "Istighfar × 100" in posts[0]
        assert h.session.last().chat_id == GROUP.id
        assert h.session.last().reply_markup.inline_keyboard[0][0].url == (
            "https://t.me/zikr_test_bot/app"
        )

        await h.tick(NIGHT_UTC.replace(minute=7))  # a late tick still posts within the grace
        night = h.session.texts()[-1]
        assert "today's summary" in night
        assert "Bob — 2/8" in night
        assert "Alice" not in night  # logged nothing
        assert await h.fetch("SELECT kind FROM group_posts ORDER BY kind") == [
            ("morning",),
            ("night",),
        ]

    run(scenario)


def test_tick_skips_unclaimed_groups_and_deactivates_kicked_ones():
    async def scenario(h: Harness) -> None:
        await h.bot_added(by=BOB)  # registered, but nobody ran /setup -> no posts
        sent_before = len(h.session.texts())
        await h.tick(MORNING_UTC)
        assert len(h.session.texts()) == sent_before

        await h.feed(_message(GROUP, ALICE, "/setup"))
        h.session.forbidden_chats.add(GROUP.id)
        await h.tick(MORNING_UTC)
        assert await h.fetch("SELECT active FROM `groups`") == [(0,)]

    run(scenario)


def test_today_shows_own_progress():
    async def scenario(h: Harness) -> None:
        await _set_up_group_with_members(h)
        await h.feed(_message(GROUP, BOB, "/today"))
        assert "Bob, today: 0/8" in h.session.last().text

        await h.feed(_message(GROUP, TgUser(id=103, is_bot=False, first_name="Cara"), "/today"))
        assert "/join" in h.session.last().text

    run(scenario)
