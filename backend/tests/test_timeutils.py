"""Tests for Swedish local-time conversion."""

from app.timeutils import to_local_time


def test_to_local_time_returns_none_for_none() -> None:
    """Missing timestamps produce no display time."""
    assert to_local_time(None) is None


def test_to_local_time_handles_summer_time() -> None:
    """Summer timestamps use Swedish summer time."""
    assert to_local_time("2026-09-29T05:09:44Z") == "07:09"


def test_to_local_time_handles_winter_time() -> None:
    """Winter timestamps use Swedish standard time."""
    assert to_local_time("2026-01-15T12:00:00Z") == "13:00"
