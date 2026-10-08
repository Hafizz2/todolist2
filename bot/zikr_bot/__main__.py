"""Entry point: `python -m zikr_bot` (run from the bot/ directory). Long polling."""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand, MenuButtonWebApp, WebAppInfo

from .config import load_settings
from .db import create_pool
from .handlers import build_router
from .middlewares import UserMiddleware
from .repo import Repo


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    settings = load_settings()
    pool = await create_pool(settings)

    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(repo=Repo(pool), settings=settings)
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())
    dp.include_router(build_router())

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Start / ጀምር"),
            BotCommand(command="setup", description="Set up this group / ግሩፑን አዘጋጅ"),
            BotCommand(command="join", description="Join the challenge / ውድድሩን ተቀላቀል"),
        ]
    )
    # The menu button in private chats opens the Mini App directly.
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="Zikr Circle", web_app=WebAppInfo(url=settings.miniapp_url)
        )
    )
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        pool.close()
        await pool.wait_closed()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
