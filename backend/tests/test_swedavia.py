"""Tests for Swedavia response handling without network calls."""

import asyncio
import json
from pathlib import Path
from typing import Any

import pytest

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
