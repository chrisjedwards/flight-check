"""Tests for the health endpoint."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    """Health endpoint returns the expected status."""
    client = TestClient(app)
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
