"""Tests for security queue wait times without network calls."""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from app import main as main_module
from app import waittime
from app.waittime import (
    WaitTimeError,
    get_flight_wait_times,
    get_wait_times,
    simplify_station,
    sort_stations,
)

DOCS_DIR = Path(__file__).resolve().parents[2] / "docs"
REAL_ASYNC_CLIENT = httpx.AsyncClient
FAKE_KEY = "test-key-not-real"


def load_sample(name: str) -> dict[str, Any]:
    with (DOCS_DIR / name).open(encoding="utf-8") as sample_file:
        return json.load(sample_file)


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    waittime._wait_time_cache.clear()


def use_transport(monkeypatch: pytest.MonkeyPatch, handler) -> None:
    """Send all WaitTime requests to a local handler instead of the network."""
    monkeypatch.setenv("SWEDAVIA_WAITTIME_KEY", FAKE_KEY)
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: REAL_ASYNC_CLIENT(transport=httpx.MockTransport(handler), **kwargs),
    )


def fail_on_request(request: httpx.Request) -> httpx.Response:
    raise AssertionError(f"Unexpected HTTP call: {request.url}")


def test_simplify_station_from_arn_sample() -> None:
    """A real ARN entry keeps minutes and FastTrack and gets Swedish local time."""
    entries = load_sample("sample-waittime-arn.json")["waitTimes"]
    regular = simplify_station(entries[0])
    fast_track = simplify_station(entries[1])

    assert regular["name"] == "Security Terminal 2"
    assert regular["label"] == "T2"
    assert regular["minutes"] == 4
    assert regular["isFastTrack"] is False
    assert regular["overflow"] is False
    assert regular["measuredLocal"] == "15:27"  # 13:27 UTC in summer time
    assert fast_track["isFastTrack"] is True


def test_station_without_terminal_uses_queue_name() -> None:
    """BMA has no terminal, so the label is the queue name without 'Security '."""
    station = simplify_station(load_sample("sample-waittime-bma.json")["waitTimes"][0])

    assert station["terminal"] is None
    assert station["label"] == "Bromma"


def test_stations_sorted_by_terminal_then_regular_before_fast_track() -> None:
    """Sorting groups terminals and puts regular queues before FastTrack."""
    entries = load_sample("sample-waittime-arn.json")["waitTimes"]
    stations = sort_stations([simplify_station(entry) for entry in reversed(entries)])

    assert [(station["terminal"], station["isFastTrack"]) for station in stations] == [
        ("T2", False),
        ("T2", True),
        ("T3", False),
        ("T4", False),
        ("T4", True),
        ("T5", False),
        ("T5", True),
    ]


def test_unsupported_airport_returns_supported_false_without_http(monkeypatch: pytest.MonkeyPatch) -> None:
    """Airports without wait times answer directly, without calling Swedavia."""
    use_transport(monkeypatch, fail_on_request)

    result = asyncio.run(get_wait_times("MMX"))

    assert result["supported"] is False
    assert result["configured"] is True
    assert result["stations"] == []


def test_missing_key_returns_configured_false_without_http(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without a key the feature is turned off instead of crashing."""
    use_transport(monkeypatch, fail_on_request)
    monkeypatch.delenv("SWEDAVIA_WAITTIME_KEY")

    result = asyncio.run(get_wait_times("ARN"))

    assert result["supported"] is True
    assert result["configured"] is False
    assert result["stations"] == []


@pytest.mark.parametrize("airport", ["XXX", ""])
def test_invalid_airport_raises_error(airport: str) -> None:
    with pytest.raises(ValueError):
        asyncio.run(get_wait_times(airport))


def test_get_wait_times_uses_response_and_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """A successful response is simplified, sorted, and cached for later calls."""
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(200, json=load_sample("sample-waittime-arn.json"))

    use_transport(monkeypatch, handler)
    result = asyncio.run(get_wait_times("arn"))
    asyncio.run(get_wait_times("ARN"))

    assert len(calls) == 1
    assert calls[0].url.path == "/waittimepublic/v2/airports/ARN"
    assert calls[0].headers["Accept"] == "application/json"
    assert result["airport"] == "ARN"
    assert result["measuredLocal"] == "15:27"
    assert len(result["stations"]) == 7


def test_unknown_flight_returns_empty_stations(monkeypatch: pytest.MonkeyPatch) -> None:
    """Swedavia's 400 for an unknown flight means 'no data', not an error."""
    use_transport(
        monkeypatch,
        lambda request: httpx.Response(400, json="No departure flightdata found for XX0000 at ARN on the 2026-09-29"),
    )

    result = asyncio.run(get_flight_wait_times("ARN", "xx0000", "2026-09-29"))

    assert result["supported"] is True
    assert result["stations"] == []


def test_other_400_is_an_error_and_logged_without_key(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Any other 400 is raised and logged with status and body, never the key."""
    use_transport(monkeypatch, lambda request: httpx.Response(400, json="Airport ARN not supported"))

    with caplog.at_level(logging.WARNING, logger="app.waittime"):
        with pytest.raises(WaitTimeError):
            asyncio.run(get_flight_wait_times("ARN", "SK1", "2026-09-29"))

    assert "400" in caplog.text
    assert "Airport ARN not supported" in caplog.text
    assert FAKE_KEY not in caplog.text


@pytest.mark.parametrize("status", [401, 500, 503])
def test_server_and_auth_errors_raise(monkeypatch: pytest.MonkeyPatch, status: int) -> None:
    use_transport(monkeypatch, lambda request: httpx.Response(status, text="error"))

    with pytest.raises(WaitTimeError):
        asyncio.run(get_wait_times("ARN"))


def test_timeout_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    use_transport(monkeypatch, handler)

    with pytest.raises(WaitTimeError):
        asyncio.run(get_wait_times("ARN"))


def test_waittimes_endpoint_returns_result(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = {"airport": "ARN", "supported": True, "configured": True, "measuredLocal": "15:27", "stations": []}

    async def fake_get_wait_times(airport: str) -> dict[str, Any]:
        return expected

    monkeypatch.setattr(main_module, "get_wait_times", fake_get_wait_times)
    response = TestClient(main_module.app).get("/api/waittimes/ARN")

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.parametrize(
    ("error", "status"),
    [(ValueError("Unknown airport: XXX"), 400), (WaitTimeError("WaitTime API error: 500"), 502)],
)
def test_waittimes_endpoint_maps_errors(monkeypatch: pytest.MonkeyPatch, error: Exception, status: int) -> None:
    async def fake_get_wait_times(airport: str) -> dict[str, Any]:
        raise error

    monkeypatch.setattr(main_module, "get_wait_times", fake_get_wait_times)
    response = TestClient(main_module.app).get("/api/waittimes/XXX")

    assert response.status_code == status
    assert response.json()["detail"] == str(error)


def test_flight_waittimes_endpoint_passes_parameters(monkeypatch: pytest.MonkeyPatch) -> None:
    received = []

    async def fake_get_flight_wait_times(airport: str, flight_id: str, date: str) -> dict[str, Any]:
        received.append((airport, flight_id, date))
        return {"airport": airport, "supported": True, "configured": True, "measuredLocal": None, "stations": []}

    monkeypatch.setattr(main_module, "get_flight_wait_times", fake_get_flight_wait_times)
    client = TestClient(main_module.app)

    assert client.get("/api/waittimes/ARN/flights/SK1420?date=2026-09-29").status_code == 200
    assert received == [("ARN", "SK1420", "2026-09-29")]
    assert client.get("/api/waittimes/ARN/flights/SK1420?date=2026-13-45").status_code == 422
