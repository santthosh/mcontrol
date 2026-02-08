"""Health check endpoint."""

from fastapi import APIRouter

from app.lib.firebase import get_firestore_client

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict:
    """Return API health status with Firestore connectivity check."""
    firestore_status = "ok"
    try:
        # Attempt a simple Firestore operation to verify connectivity
        db = get_firestore_client()
        # List collections is a lightweight operation to verify connection
        list(db.collections())
    except Exception:
        firestore_status = "error"

    overall_status = "ok" if firestore_status == "ok" else "degraded"

    return {
        "status": overall_status,
        "version": "0.0.1",
        "services": {
            "firestore": firestore_status,
        },
    }
