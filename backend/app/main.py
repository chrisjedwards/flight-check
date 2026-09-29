"""FastAPI application entry point."""

from pathlib import Path
from datetime import date

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app.swedavia import get_flights, simplify_flight

app = FastAPI(title="Flight Check")
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Return the basic service health status."""
    return {"status": "ok"}


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

    return [simplify_flight(flight, direction) for flight in flights]


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
