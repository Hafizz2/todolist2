from __future__ import annotations

import aiomysql

from .config import Settings


async def create_pool(settings: Settings) -> aiomysql.Pool:
    return await aiomysql.create_pool(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_pass,
        db=settings.db_name,
        charset="utf8mb4",
        autocommit=True,
        minsize=1,
        maxsize=5,
        pool_recycle=3600,
    )
