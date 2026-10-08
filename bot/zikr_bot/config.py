from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_pass: str
    miniapp_url: str


def load_settings() -> Settings:
    load_dotenv()

    def required(key: str) -> str:
        value = os.environ.get(key, "").strip()
        if not value:
            raise RuntimeError(f"Missing required setting {key} (see bot/.env.example)")
        return value

    return Settings(
        bot_token=required("BOT_TOKEN"),
        db_host=os.environ.get("DB_HOST", "127.0.0.1"),
        db_port=int(os.environ.get("DB_PORT", "3306")),
        db_name=required("DB_NAME"),
        db_user=required("DB_USER"),
        db_pass=os.environ.get("DB_PASS", ""),
        miniapp_url=required("MINIAPP_URL"),
    )
