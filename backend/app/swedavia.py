"""Swedavia FlightInfo API access and flight data simplification."""

import os
import time
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

from app.timeutils import to_local_time

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

BASE_URL = "https://api.swedavia.se/flightinfo/v2"
CACHE_SECONDS = 60
AIRPORTS: dict[str, str] = {
    "ARN": "Stockholm Arlanda",
    "GOT": "Göteborg Landvetter",
    "BMA": "Stockholm Bromma",
    "MMX": "Malmö",
    "LLA": "Luleå",
    "UME": "Umeå",
    "OSD": "Östersund",
    "VBY": "Visby",
    "RNB": "Ronneby",
    "KRN": "Kiruna",
}
DIRECTIONS = {"arrivals", "departures"}
_flight_cache: dict[tuple[str, str, str], tuple[float, list[dict[str, Any]]]] = {}


def _headers() -> dict[str, str]:
    """Build request headers without exposing the subscription key."""
    api_key = os.getenv("SWEDAVIA_API_KEY")
    if not api_key:
        raise RuntimeError("SWEDAVIA_API_KEY is missing from backend/.env")
    return {
        "Ocp-Apim-Subscription-Key": api_key,
        "Accept": "application/json",
    }


async def get_flights(airport: str, direction: str, date: str) -> list[dict[str, Any]]:
    """Get and cache flights for an airport, direction, and date."""
    airport = airport.upper()
    if airport not in AIRPORTS:
        raise ValueError(f"Unknown airport: {airport}")
    if direction not in DIRECTIONS:
        raise ValueError(f"Unknown direction: {direction}")

    cache_key = (airport, direction, date)
    cached = _flight_cache.get(cache_key)
    if cached and time.monotonic() - cached[0] < CACHE_SECONDS:
        return cached[1]

    url = f"{BASE_URL}/{airport}/{direction}/{date}"
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(url, headers=_headers())
        response.raise_for_status()

    flights = response.json().get("flights", [])
    _flight_cache[cache_key] = (time.monotonic(), flights)
    return flights


def simplify_flight(flight: dict[str, Any], direction: str) -> dict[str, Any]:
    """Return the display fields for one arrival or departure."""
    if direction == "arrivals":
        city = flight.get("departureAirportEnglish")
        flight_time = flight.get("arrivalTime") or {}
    else:
        city = flight.get("arrivalAirportEnglish")
        flight_time = flight.get("departureTime") or {}

    airline_operator = flight.get("airlineOperator") or {}
    location_status = flight.get("locationAndStatus") or {}
    baggage_info = flight.get("baggage") or {}

    return {
        "flightId": flight.get("flightId"),
        "airline": airline_operator.get("name"),
        "city": city,
        "scheduled": to_local_time(flight_time.get("scheduledUtc")),
        "estimated": to_local_time(flight_time.get("estimatedUtc")),
        "actual": to_local_time(flight_time.get("actualUtc")),
        "terminal": location_status.get("terminal"),
        "gate": location_status.get("gate"),
        "status": location_status.get("flightLegStatus"),
        "statusText": location_status.get("flightLegStatusEnglish"),
        "baggage": baggage_info.get("baggageClaimUnit"),
        "region": flight.get("diIndicator"),
    }
