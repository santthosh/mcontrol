"""Firebase SDK initialization with emulator support."""

import os
from typing import TYPE_CHECKING

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Client as FirestoreClient

if TYPE_CHECKING:
    from google.cloud.firestore_v1 import Client

from app.lib.config import get_settings

# Cached client instance
_firestore_client: "Client | None" = None


def _initialize_app() -> firebase_admin.App | None:
    """Initialize Firebase Admin SDK with project configuration."""
    # Check if already initialized
    try:
        return firebase_admin.get_app()
    except ValueError:
        pass

    settings = get_settings()
    emulator_host = os.environ.get("FIRESTORE_EMULATOR_HOST")

    # When running against emulator, we don't need firebase_admin initialization
    # The google-cloud-firestore client will auto-detect FIRESTORE_EMULATOR_HOST
    if emulator_host:
        return None

    # Production mode - use default credentials
    cred = credentials.ApplicationDefault()
    app = firebase_admin.initialize_app(
        cred, options={"projectId": settings.firebase_project_id}
    )
    return app


def get_firestore_client() -> "Client":
    """Get Firestore client instance."""
    global _firestore_client

    if _firestore_client is not None:
        return _firestore_client

    settings = get_settings()
    emulator_host = os.environ.get("FIRESTORE_EMULATOR_HOST")

    if emulator_host:
        # Emulator mode - create client directly without credentials
        # google-cloud-firestore auto-detects FIRESTORE_EMULATOR_HOST
        _firestore_client = FirestoreClient(project=settings.firebase_project_id)
    else:
        # Production mode - use firebase_admin's client
        _initialize_app()
        _firestore_client = firestore.client()

    return _firestore_client
