"""Utilities for converting flight timestamps to local time."""

from datetime import datetime
from zoneinfo import ZoneInfo


def parse_utc(utc_string: str | None) -> datetime | None:
    """Parse an ISO UTC timestamp, returning None when it is missing."""
    if not utc_string or not utc_string.strip():
        return None
    return datetime.fromisoformat(utc_string.replace("Z", "+00:00"))


def to_local_time(utc_string: str | None) -> str | None:
    """Convert a UTC ISO timestamp to Europe/Stockholm time."""
    utc_time = parse_utc(utc_string)
    if utc_time is None:
        return None

    return utc_time.astimezone(ZoneInfo("Europe/Stockholm")).strftime("%H:%M")
