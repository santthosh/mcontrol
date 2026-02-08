"""Firebase SDK initialization with emulator support."""

import os
from typing import TYPE_CHECKING

import firebase_admin
from firebase_admin import credentials, firestore

if TYPE_CHECKING:
    from google.cloud.firestore_v1 import Client

from app.lib.config import get_settings

# Track if we've initialized
_initialized = False


def _initialize_app() -> firebase_admin.App:
    """Initialize Firebase Admin SDK with project configuration."""
    global _initialized

    # Check if already initialized
    try:
        return firebase_admin.get_app()
    except ValueError:
        pass

    settings = get_settings()
    emulator_host = os.environ.get("FIRESTORE_EMULATOR_HOST")

    # Initialize with project ID
    # When running against emulator, no credentials needed
    # In production, use default credentials (ADC)
    if emulator_host:
        # Emulator mode - no credentials needed, use mock credentials
        app = firebase_admin.initialize_app(
            credential=None,
            options={"projectId": settings.firebase_project_id},
        )
    else:
        # Production mode - use default credentials
        cred = credentials.ApplicationDefault()
        app = firebase_admin.initialize_app(
            cred, options={"projectId": settings.firebase_project_id}
        )

    _initialized = True
    return app


def get_firestore_client() -> "Client":
    """Get Firestore client instance."""
    _initialize_app()
    return firestore.client()
