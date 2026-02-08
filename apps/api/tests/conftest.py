"""pytest fixtures for API tests."""

import os

import pytest
from fastapi.testclient import TestClient

# Ensure emulator environment is set for tests
os.environ.setdefault("FIRESTORE_EMULATOR_HOST", "localhost:8080")
os.environ.setdefault("FIREBASE_AUTH_EMULATOR_HOST", "localhost:9099")
os.environ.setdefault("FIREBASE_PROJECT_ID", "mcontrol-dev")

from app.main import app  # noqa: E402


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)
