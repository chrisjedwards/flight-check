"""FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Flight Check")
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Return the basic service health status."""
    return {"status": "ok"}


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
