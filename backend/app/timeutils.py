"""Utilities for converting flight timestamps to local time."""

from datetime import datetime
from zoneinfo import ZoneInfo


def to_local_time(utc_string: str | None) -> str | None:
    """Convert a UTC ISO timestamp to Europe/Stockholm time."""
    if not utc_string or not utc_string.strip():
        return None

    utc_time = datetime.fromisoformat(utc_string.replace("Z", "+00:00"))
    return utc_time.astimezone(ZoneInfo("Europe/Stockholm")).strftime("%H:%M")
