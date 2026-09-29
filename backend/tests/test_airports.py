"""Tests for airport country lookup and the airport API endpoint."""

import logging

import pytest
from fastapi.testclient import TestClient

from app.airports import lookup_airport
from app.main import app
from app.swedavia import AIRPORTS


def test_lookup_airport_lhr() -> None:
    """Heathrow lookup returns its country metadata."""
    airport = lookup_airport("LHR")

    assert airport is not None
    assert airport["country"] == "United Kingdom"
    assert airport["countryCode"] == "GB"
    assert airport["continent"] == "EU"
    assert isinstance(airport["lat"], (int, float))
    assert isinstance(airport["lon"], (int, float))


def test_lookup_airport_got() -> None:
    """Landvetter lookup returns its country metadata."""
    airport = lookup_airport("GOT")

    assert airport is not None
    assert airport["country"] == "Sweden"
    assert airport["countryCode"] == "SE"


def test_lookup_airport_unknown_or_missing() -> None:
    """Unknown and missing IATA codes return no record."""
    assert lookup_airport("ZZZ") is None
    assert lookup_airport(None) is None


def test_unknown_iata_code_is_logged_once(caplog: pytest.LogCaptureFixture) -> None:
    """Repeated unknown codes produce only one warning."""
    with caplog.at_level(logging.WARNING, logger="app.airports"):
        assert lookup_airport("QQQ") is None
        assert lookup_airport("QQQ") is None

    matching_warnings = [
        record.message
        for record in caplog.records
        if record.message == "Unknown IATA code: QQQ, consider regenerating airport data"
    ]
    assert matching_warnings == ["Unknown IATA code: QQQ, consider regenerating airport data"]


def test_all_swedavia_airports_are_in_dataset() -> None:
    """Every supported Swedavia airport has a generated record."""
    missing_airports = [code for code in AIRPORTS if lookup_airport(code) is None]
    assert missing_airports == []


def test_airports_endpoint_returns_ten_airports() -> None:
    """Airport endpoint returns all supported Swedavia airports."""
    response = TestClient(app).get("/api/airports")

    assert response.status_code == 200
    airports = response.json()
    assert len(airports) == 10
    assert airports[0] == {"code": "ARN", "name": "Stockholm Arlanda"}