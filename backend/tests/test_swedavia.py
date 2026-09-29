"""Tests for Swedavia response handling without network calls."""

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app import main as main_module
from app.airports import lookup_airport
from app.swedavia import get_flights, simplify_flight

SAMPLE_ARRIVALS = Path(__file__).resolve().parents[2] / "docs" / "sample-arrivals.json"


@pytest.fixture(scope="module")
def sample_flights() -> list[dict[str, Any]]:
    """Load the saved real arrivals response."""
    with SAMPLE_ARRIVALS.open(encoding="utf-8") as sample_file:
        return json.load(sample_file)["flights"]


def test_simplify_landed_flight_with_actual_time(sample_flights: list[dict[str, Any]]) -> None:
    """A landed sample flight retains its converted actual time."""
    landed_flight = next(
        (
            flight
            for flight in sample_flights
            if (flight.get("locationAndStatus") or {}).get("flightLegStatus") == "LAN"
            and (flight.get("arrivalTime") or {}).get("actualUtc")
        ),
        None,
    )

    assert landed_flight is not None
    simplified = simplify_flight(landed_flight, "arrivals")
    assert simplified["status"] == "LAN"
    assert simplified["actual"] is not None
    assert simplified["isUpcoming"] is False


def test_simplify_scheduled_flight_is_upcoming(sample_flights: list[dict[str, Any]]) -> None:
    """A scheduled flight without an actual time is upcoming."""
    scheduled_flight = next(
        (
            flight
            for flight in sample_flights
            if (flight.get("locationAndStatus") or {}).get("flightLegStatus") == "SCH"
            and not (flight.get("arrivalTime") or {}).get("actualUtc")
        ),
        None,
    )

    assert scheduled_flight is not None
    assert simplify_flight(scheduled_flight, "arrivals")["isUpcoming"] is True


def test_cancelled_flight_is_marked(sample_flights: list[dict[str, Any]]) -> None:
    """The known cancelled sample flight is marked as cancelled."""
    cancelled_flight = next(flight for flight in sample_flights if flight.get("flightId") == "SK2182")
    assert simplify_flight(cancelled_flight, "arrivals")["isCancelled"] is True


def test_delay_minutes_are_calculated(sample_flights: list[dict[str, Any]]) -> None:
    """Delay is estimated time minus scheduled time in whole minutes."""
    flight = next(flight for flight in sample_flights if flight.get("flightId") == "BLX158")
    simplified = simplify_flight(flight, "arrivals")

    assert simplified["delayMinutes"] == 85
    assert simplified["scheduledUtc"] == "2026-09-29T13:35:00Z"


def test_lhr_flight_includes_country(sample_flights: list[dict[str, Any]]) -> None:
    """A flight from Heathrow resolves country through its IATA code."""
    flight = next(
        flight
        for flight in sample_flights
        if (flight.get("flightLegIdentifier") or {}).get("departureAirportIata") == "LHR"
    )
    simplified = simplify_flight(flight, "arrivals")

    assert simplified["cityIata"] == "LHR"
    assert simplified["country"] == "United Kingdom"
    assert simplified["countryCode"] == "GB"
    assert simplified["continent"] == "Europe"


def test_all_sample_other_airports_exist(sample_flights: list[dict[str, Any]]) -> None:
    """Every other-airport code in saved arrivals has a lookup record."""
    airport_codes = {
        identifier["departureAirportIata"].strip().upper()
        for flight in sample_flights
        if (identifier := flight.get("flightLegIdentifier") or {}).get("departureAirportIata")
    }
    missing_codes = sorted(code for code in airport_codes if lookup_airport(code) is None)

    assert missing_codes == []


def test_flights_endpoint_sorts_by_scheduled_utc(
    monkeypatch: pytest.MonkeyPatch, sample_flights: list[dict[str, Any]]
) -> None:
    """The endpoint sorts simplified flights using their raw UTC timestamps."""
    flights = [
        next(flight for flight in sample_flights if flight.get("flightId") == flight_id)
        for flight_id in ("BLX158", "SK2182")
    ]

    async def fake_get_flights(airport: str, direction: str, date: str) -> list[dict[str, Any]]:
        return flights

    monkeypatch.setattr(main_module, "get_flights", fake_get_flights)
    response = TestClient(main_module.app).get("/api/flights/ARN/arrivals/2026-09-29")

    assert response.status_code == 200
    scheduled_utc = [flight["scheduledUtc"] for flight in response.json()]
    assert scheduled_utc == sorted(scheduled_utc)


def test_simplify_flight_without_gate(sample_flights: list[dict[str, Any]]) -> None:
    """A missing gate remains None for the frontend to display."""
    flight_without_gate = next(
        (
            flight
            for flight in sample_flights
            if "gate" not in (flight.get("locationAndStatus") or {})
        ),
        None,
    )

    assert flight_without_gate is not None
    assert simplify_flight(flight_without_gate, "arrivals")["gate"] is None


@pytest.mark.parametrize(
    ("airport", "direction", "message"),
    [
        ("XXX", "arrivals", "Unknown airport: XXX"),
        ("ARN", "sideways", "Unknown direction: sideways"),
    ],
)
def test_get_flights_rejects_invalid_parameters_without_network(
    airport: str, direction: str, message: str
) -> None:
    """Invalid query parameters fail before any API request."""
    with pytest.raises(ValueError, match=message):
        asyncio.run(get_flights(airport, direction, "2026-09-29"))
