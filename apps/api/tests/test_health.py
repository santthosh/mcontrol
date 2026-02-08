"""Tests for health endpoint."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test health endpoint returns ok status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    # Print debug info if status is not ok
    if data["status"] != "ok":
        print(f"Health check response: {data}")
    assert data["status"] == "ok", f"Expected 'ok' but got '{data['status']}'. Debug: {data.get('debug', 'no debug info')}"
    assert data["version"] == "0.0.1"
