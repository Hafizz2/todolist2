from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .i18n import t

LANG_LABELS = {"am": "🇪🇹 አማርኛ", "en": "🇬🇧 English"}

GROUP_START_PREFIX = "group_"


def miniapp_link(bot_username: str, short_name: str, start_param: str | None = None) -> str:
    """Direct Mini App link (https://core.telegram.org/bots/webapps#direct-link-mini-apps).

    Unlike web_app buttons these work in group chats, and Telegram still signs initData.
    `start_param` reaches the Mini App as initData's `start_param`.
    """
    link = f"https://t.me/{bot_username}/{short_name}"
    return f"{link}?startapp={start_param}" if start_param else link


def group_start_param(group_id: int) -> str:
    """start_param that opens the Mini App in group-config mode for `group_id`."""
    return f"{GROUP_START_PREFIX}{group_id}"


def _link_button(text: str, url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, url=url)]])


def start_keyboard(lang: str, bot_username: str, short_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=label, callback_data=f"lang:{code}")
                for code, label in LANG_LABELS.items()
            ],
            [
                InlineKeyboardButton(
                    text=t(lang, "btn_open_app"), url=miniapp_link(bot_username, short_name)
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(lang, "btn_add_to_group"),
                    url=f"https://t.me/{bot_username}?startgroup=true",
                )
            ],
        ]
    )


def open_app_keyboard(lang: str, bot_username: str, short_name: str) -> InlineKeyboardMarkup:
    return _link_button(t(lang, "btn_open_app"), miniapp_link(bot_username, short_name))


def open_settings_keyboard(
    lang: str, bot_username: str, short_name: str, group_id: int
) -> InlineKeyboardMarkup:
    """Opens the Mini App in group-config mode. The Mini App enforces owner-only access."""
    url = miniapp_link(bot_username, short_name, group_start_param(group_id))
    return _link_button(t(lang, "btn_open_settings"), url)
