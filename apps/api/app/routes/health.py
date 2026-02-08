"""Health check endpoint."""

import os

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Return API health status.

    This endpoint is used by Cloud Run startup/liveness probes.
    Returns 200 as long as the API is running - Firestore connectivity
    is checked separately in /health/ready.
    """
    return {
        "status": "ok",
        "version": "0.0.1",
    }


@router.get("/health/ready")
async def readiness_check() -> dict:
    """Check if all services are ready (including Firestore)."""
    from app.lib.firebase import get_firestore_client

    firestore_status = "ok"
    firestore_error = None
    try:
        db = get_firestore_client()
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

    if firestore_error:
        result["debug"] = {
            "firestore_error": firestore_error,
            "emulator_host": os.environ.get("FIRESTORE_EMULATOR_HOST", "not set"),
        }

    return result
