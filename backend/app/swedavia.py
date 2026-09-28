"""Placeholders for Swedavia FlightInfo API access."""

from typing import Any

BASE_URL = "https://api.swedavia.se/flightinfo/v2"
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


async def get_flights(airport: str, direction: str, date: str) -> Any:
    """Get an airport's arrivals or departures for a date."""
    # TODO: Implement the asynchronous Swedavia API request.
    pass


async def get_flight(flight_id: str, date: str) -> Any:
    """Get details for one flight on a date."""
    # TODO: Implement the asynchronous Swedavia API request.
    pass
