"""FastAPI application entry point."""

from pathlib import Path
from datetime import date

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app.swedavia import AIRPORTS, get_flights, simplify_flight
from app.waittime import WaitTimeError, get_flight_wait_times, get_wait_times

app = FastAPI(title="Flight Check")
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Return the basic service health status."""
    return {"status": "ok"}


@app.get("/api/airports")
async def list_airports() -> list[dict[str, str]]:
    """Return the supported Swedavia airports."""
    return [{"code": code, "name": name} for code, name in AIRPORTS.items()]


@app.get("/api/flights/{airport}/{direction}/{day}")
async def list_flights(airport: str, direction: str, day: date) -> list[dict]:
    """Return simplified arrivals or departures for a date."""
    try:
        flights = await get_flights(airport, direction, day.isoformat())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except httpx.HTTPStatusError as error:
        message = f"Swedavia API error: {error.response.status_code}"
        raise HTTPException(status_code=502, detail=message) from error

    simplified_flights = [simplify_flight(flight, direction) for flight in flights]
    return sorted(
        simplified_flights,
        key=lambda flight: (flight.get("scheduledUtc") is None, flight.get("scheduledUtc") or ""),
    )


@app.get("/api/waittimes/{airport}")
async def list_wait_times(airport: str) -> dict:
    """Return security queue wait times for an airport."""
    try:
        return await get_wait_times(airport)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except WaitTimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


@app.get("/api/waittimes/{airport}/flights/{flight_id}")
async def list_flight_wait_times(airport: str, flight_id: str, date: date) -> dict:
    """Return the security queues near one departing flight's gate."""
    try:
        return await get_flight_wait_times(airport, flight_id, date.isoformat())
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except WaitTimeError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
