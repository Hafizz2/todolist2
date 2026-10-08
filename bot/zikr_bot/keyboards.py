from __future__ import annotations

from urllib.parse import urlencode, urlsplit, urlunsplit

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from .i18n import t

LANG_LABELS = {"am": "🇪🇹 አማርኛ", "en": "🇬🇧 English"}

SETUP_PAYLOAD_PREFIX = "setup_"


def with_query(url: str, **params: object) -> str:
    """Append query parameters to `url`, keeping any it already has."""
    parts = urlsplit(url)
    extra = urlencode(params)
    query = f"{parts.query}&{extra}" if parts.query else extra
    return urlunsplit(parts._replace(query=query))


def setup_payload(group_id: int) -> str:
    return f"{SETUP_PAYLOAD_PREFIX}{group_id}"


def parse_setup_payload(payload: str | None) -> int | None:
    """`setup_<group_id>` deep-link payload -> group id, or None if it isn't one."""
    if not payload or not payload.startswith(SETUP_PAYLOAD_PREFIX):
        return None
    rest = payload[len(SETUP_PAYLOAD_PREFIX) :]
    return int(rest) if rest.isdigit() else None


def start_keyboard(lang: str, bot_username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=label, callback_data=f"lang:{code}")
                for code, label in LANG_LABELS.items()
            ],
            [
                InlineKeyboardButton(
                    text=t(lang, "btn_add_to_group"),
                    url=f"https://t.me/{bot_username}?startgroup=true",
                )
            ],
        ]
    )


def open_settings_link_keyboard(
    lang: str, bot_username: str, group_id: int
) -> InlineKeyboardMarkup:
    """Group-chat button. Telegram doesn't allow web_app buttons in groups, so this deep-links
    the owner into a private chat with the bot, which then offers the real Mini App button."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(lang, "btn_open_settings"),
                    url=f"https://t.me/{bot_username}?start={setup_payload(group_id)}",
                )
            ]
        ]
    )


def settings_webapp_keyboard(lang: str, miniapp_url: str, group_id: int) -> InlineKeyboardMarkup:
    """Private-chat button that opens the Mini App in group-config mode."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t(lang, "btn_open_settings"),
                    web_app=WebAppInfo(url=with_query(miniapp_url, group=group_id)),
                )
            ]
        ]
    )
