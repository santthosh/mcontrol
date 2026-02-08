"""Health check endpoint."""

import os

from fastapi import APIRouter

from app.lib.firebase import get_firestore_client

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Return API health status with Firestore connectivity check."""
    firestore_status = "ok"
    firestore_error = None
    try:
        # Attempt a simple Firestore operation to verify connectivity
        db = get_firestore_client()
        # List collections is a lightweight operation to verify connection
        list(db.collections())
    except Exception as e:
        firestore_status = "error"
        firestore_error = str(e)

    overall_status = "ok" if firestore_status == "ok" else "degraded"

    result: dict = {
        "status": overall_status,
        "version": "0.0.1",
        "services": {
            "firestore": firestore_status,
        },
    }

    # Include debug info if there's an error (useful for CI debugging)
    if firestore_error:
        result["debug"] = {
            "firestore_error": firestore_error,
            "emulator_host": os.environ.get("FIRESTORE_EMULATOR_HOST", "not set"),
        }

    return result
