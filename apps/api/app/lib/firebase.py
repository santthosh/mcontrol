"""Firebase SDK initialization with emulator support."""

import os
from functools import lru_cache
from typing import TYPE_CHECKING

import firebase_admin
from firebase_admin import credentials, firestore

if TYPE_CHECKING:
    from google.cloud.firestore_v1 import Client

from app.lib.config import get_settings


def _initialize_app() -> firebase_admin.App:
    """Initialize Firebase Admin SDK with project configuration."""
    settings = get_settings()

    # Check if already initialized
    try:
        return firebase_admin.get_app()
    except ValueError:
        pass

    # Initialize with project ID
    # When running against emulator, no credentials needed
    # In production, use default credentials (ADC)
    if os.environ.get("FIRESTORE_EMULATOR_HOST"):
        # Emulator mode - no credentials needed
        app = firebase_admin.initialize_app(options={"projectId": settings.firebase_project_id})
    else:
        # Production mode - use default credentials
        cred = credentials.ApplicationDefault()
        app = firebase_admin.initialize_app(
            cred, options={"projectId": settings.firebase_project_id}
        )

    return app


@lru_cache
def get_firestore_client() -> "Client":
    """Get cached Firestore client instance."""
    _initialize_app()
    return firestore.client()
