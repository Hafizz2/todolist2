from __future__ import annotations

import json
from pathlib import Path

DEFAULT_LANG = "am"
SUPPORTED_LANGS = ("am", "en")

_LOCALES_DIR = Path(__file__).resolve().parent.parent / "locales"


def _load() -> dict[str, dict[str, str]]:
    return {
        lang: json.loads((_LOCALES_DIR / f"{lang}.json").read_text(encoding="utf-8"))
        for lang in SUPPORTED_LANGS
    }


_STRINGS = _load()


def normalize_lang(lang: str | None) -> str:
    return lang if lang in SUPPORTED_LANGS else DEFAULT_LANG


def t(lang: str | None, key: str, **kwargs: object) -> str:
    """Translate `key` into `lang`, falling back to the default language, then the key."""
    template = _STRINGS[normalize_lang(lang)].get(key) or _STRINGS[DEFAULT_LANG].get(key) or key
    return template.format(**kwargs) if kwargs else template


def has_key(lang: str | None, key: str) -> bool:
    return key in _STRINGS[normalize_lang(lang)]
