"""Tests for health endpoint."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test health endpoint returns ok status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.0.1"


def test_readiness_check(client: TestClient) -> None:
    """Test readiness endpoint checks Firestore connectivity."""
    response = client.get("/api/health/ready")
    assert response.status_code == 200
    data = response.json()
    # In test environment with emulator, this should be ok
    # Print debug info if not ok
    if data["status"] != "ok":
        print(f"Readiness check response: {data}")
    assert data["status"] == "ok", (
        f"Expected 'ok' but got '{data['status']}'. Debug: {data.get('debug', 'no debug info')}"
    )
    assert data["version"] == "0.0.1"
    assert "firestore" in data["services"]
