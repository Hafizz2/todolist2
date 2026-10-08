import json
import string
from pathlib import Path

from zikr_bot.i18n import DEFAULT_LANG, SUPPORTED_LANGS, t

LOCALES = Path(__file__).resolve().parent.parent / "locales"


def _placeholders(template: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(template) if name}


def test_all_locales_have_the_same_keys_and_placeholders():
    strings = {
        lang: json.loads((LOCALES / f"{lang}.json").read_text("utf-8")) for lang in SUPPORTED_LANGS
    }
    reference = strings[DEFAULT_LANG]
    for lang, table in strings.items():
        assert table.keys() == reference.keys(), lang
        for key, template in table.items():
            assert _placeholders(template) == _placeholders(reference[key]), (lang, key)


def test_unknown_language_falls_back_to_default():
    assert t("fr", "group_only") == t(DEFAULT_LANG, "group_only")
    assert t(None, "group_only") == t(DEFAULT_LANG, "group_only")


def test_formats_placeholders():
    assert "Abdul" in t("en", "join_done", name="Abdul")
