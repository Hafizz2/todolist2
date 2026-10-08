"""Which scheduled posts are due. Pure functions, driven by the bot's one-minute tick."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_TIMEZONE = "Africa/Addis_Ababa"

# A post is still sent if the bot was down or a tick was late, up to this long after its time.
# group_posts makes sure it's sent only once per local day.
GRACE = timedelta(minutes=30)


def group_zone(name: str) -> ZoneInfo:
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        return ZoneInfo(DEFAULT_TIMEZONE)


def local_date(tz_name: str, now_utc: datetime) -> date:
    return now_utc.astimezone(group_zone(tz_name)).date()


def due_posts(
    tz_name: str, morning: time, night: time, now_utc: datetime
) -> Iterator[tuple[str, date]]:
    """Yields (kind, local_date) for each post whose time has come within the grace window."""
    zone = group_zone(tz_name)
    local = now_utc.astimezone(zone)
    for kind, at in (("morning", morning), ("night", night)):
        scheduled = datetime.combine(local.date(), at, tzinfo=zone)
        if scheduled <= local < scheduled + GRACE:
            yield kind, local.date()
