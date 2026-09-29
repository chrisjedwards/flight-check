"""Swedavia WaitTime API access for security queue wait times."""

import logging
import os
import time
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

from app.swedavia import AIRPORTS
from app.timeutils import to_local_time

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

BASE_URL = "https://api.swedavia.se/waittimepublic/v2"
CACHE_SECONDS = 60
# Verified with scripts/probe_waittime.py: the other seven airports return 400 "not supported".
SUPPORTED_AIRPORTS = {"ARN", "BMA", "GOT"}
UNKNOWN_FLIGHT_PREFIX = "No departure flightdata found"
logger = logging.getLogger(__name__)
_wait_time_cache: dict[tuple[str, ...], tuple[float, list[dict[str, Any]]]] = {}


class WaitTimeError(Exception):
    """Raised when the WaitTime API cannot provide data."""


def is_configured() -> bool:
    """Return whether the WaitTime subscription key is set."""
    return bool(os.getenv("SWEDAVIA_WAITTIME_KEY"))


def _headers() -> dict[str, str]:
    """Build request headers without exposing the subscription key."""
    return {
        "Ocp-Apim-Subscription-Key": os.getenv("SWEDAVIA_WAITTIME_KEY", ""),
        "Accept": "application/json",
    }


def simplify_station(entry: dict[str, Any]) -> dict[str, Any]:
    """Flatten one WaitTime entry into the fields the frontend needs."""
    name = entry.get("queueName") or ""
    terminal = entry.get("terminal") or None
    return {
        "name": name,
        # Stations without a terminal (BMA, GOT) use their queue name instead.
        "label": terminal or name.removeprefix("Security ").strip() or None,
        "terminal": terminal,
        "minutes": entry.get("currentProjectedWaitTime"),
        "isFastTrack": bool(entry.get("isFastTrack")),
        "overflow": bool(entry.get("overflow")),
        "measuredLocal": to_local_time(entry.get("currentTime")),
    }


def sort_stations(stations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort by terminal, with regular queues before FastTrack in each terminal."""
    return sorted(
        stations,
        key=lambda station: (
            station["terminal"] is None,
            station["terminal"] or "",
            station["isFastTrack"],
            station["name"],
        ),
    )


def _result(airport: str, supported: bool, entries: list[dict[str, Any]]) -> dict[str, Any]:
    stations = sort_stations([simplify_station(entry) for entry in entries])
    latest = max((entry.get("currentTime") or "" for entry in entries), default="")
    return {
        "airport": airport,
        "supported": supported,
        "configured": is_configured(),
        "measuredLocal": to_local_time(latest),
        "stations": stations,
    }


async def _fetch(cache_key: tuple[str, ...], path: str, params: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """Get and cache WaitTime entries, raising WaitTimeError on API problems."""
    cached = _wait_time_cache.get(cache_key)
    if cached and time.monotonic() - cached[0] < CACHE_SECONDS:
        return cached[1]

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{BASE_URL}{path}", params=params, headers=_headers())
    except httpx.RequestError as error:
        raise WaitTimeError(f"WaitTime API request failed: {type(error).__name__}") from error

    if response.status_code == 400 and response.text.strip('" ').startswith(UNKNOWN_FLIGHT_PREFIX):
        entries: list[dict[str, Any]] = []
    elif response.status_code != 200:
        # Log status and body (never the key) so unexpected answers are visible while developing.
        logger.warning("WaitTime API returned %s for %s: %s", response.status_code, path, response.text[:200])
        raise WaitTimeError(f"WaitTime API error: {response.status_code}")
    else:
        entries = response.json().get("waitTimes") or []

    _wait_time_cache[cache_key] = (time.monotonic(), entries)
    return entries


def _check_airport(airport: str) -> str:
    airport = airport.upper()
    if airport not in AIRPORTS:
        raise ValueError(f"Unknown airport: {airport}")
    return airport


async def get_wait_times(airport: str) -> dict[str, Any]:
    """Return all security queues for an airport."""
    airport = _check_airport(airport)
    if airport not in SUPPORTED_AIRPORTS or not is_configured():
        return _result(airport, airport in SUPPORTED_AIRPORTS, [])
    entries = await _fetch((airport,), f"/airports/{airport}")
    return _result(airport, True, entries)


async def get_flight_wait_times(airport: str, flight_id: str, date: str) -> dict[str, Any]:
    """Return the security queues near one departing flight's gate."""
    airport = _check_airport(airport)
    flight_id = flight_id.strip().upper()
    if not flight_id:
        raise ValueError("Flight id is missing")
    if airport not in SUPPORTED_AIRPORTS or not is_configured():
        return _result(airport, airport in SUPPORTED_AIRPORTS, [])
    entries = await _fetch(
        (airport, flight_id, date),
        f"/airports/{airport}/flights",
        {"flightid": flight_id, "date": date},
    )
    return _result(airport, True, entries)
