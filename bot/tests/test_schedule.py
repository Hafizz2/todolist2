from datetime import UTC, date, datetime, time

from zikr_bot.schedule import due_posts, local_date

ADDIS = "Africa/Addis_Ababa"  # UTC+3, no DST
MORNING, NIGHT = time(6, 0), time(21, 0)


def due(utc: datetime, tz: str = ADDIS) -> list[tuple[str, date]]:
    return list(due_posts(tz, MORNING, NIGHT, utc))


def test_morning_is_due_at_local_time():
    assert due(datetime(2026, 10, 9, 3, 0, tzinfo=UTC)) == [("morning", date(2026, 10, 9))]


def test_not_due_before_time():
    assert due(datetime(2026, 10, 9, 2, 59, tzinfo=UTC)) == []


def test_still_due_within_grace_but_not_after():
    assert due(datetime(2026, 10, 9, 3, 29, tzinfo=UTC)) == [("morning", date(2026, 10, 9))]
    assert due(datetime(2026, 10, 9, 3, 30, tzinfo=UTC)) == []


def test_night_uses_group_local_date():
    # 21:00 in Addis on Oct 9 is 18:00 UTC.
    assert due(datetime(2026, 10, 9, 18, 5, tzinfo=UTC)) == [("night", date(2026, 10, 9))]


def test_each_group_uses_its_own_timezone():
    utc = datetime(2026, 10, 9, 5, 0, tzinfo=UTC)
    assert due(utc, "Europe/London") == [("morning", date(2026, 10, 9))]  # BST, UTC+1
    assert due(utc, ADDIS) == []


def test_invalid_timezone_falls_back_to_default():
    assert due(datetime(2026, 10, 9, 3, 0, tzinfo=UTC), "Not/AZone") == [
        ("morning", date(2026, 10, 9))
    ]


def test_local_date_crosses_midnight():
    assert local_date(ADDIS, datetime(2026, 10, 9, 22, 0, tzinfo=UTC)) == date(2026, 10, 10)
