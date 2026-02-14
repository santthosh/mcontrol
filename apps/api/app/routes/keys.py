"""API routes for encrypted credential (API key) management."""

import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.lib.config import get_settings
from app.lib.crypto import encrypt, mask_key
from app.lib.firebase import get_firestore_client
from app.middleware.auth import CurrentUser
from app.models.credential import CredentialDocument
from app.repositories.credential import CredentialRepository

router = APIRouter(tags=["keys"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class CreateKeyRequest(BaseModel):
    provider: str
    name: str
    key: str


class UpdateKeyRequest(BaseModel):
    name: str | None = None
    key: str | None = None


class KeyResponse(BaseModel):
    id: str
    provider: str
    name: str
    key_hint: str
    created_at: str
    updated_at: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ensure_encryption_configured() -> None:
    """Raise 500 if the encryption key is not set."""
    if not get_settings().credential_encryption_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Credential encryption is not configured",
        )


def _to_response(doc: CredentialDocument) -> KeyResponse:
    """Convert a CredentialDocument to the API response model."""
    return KeyResponse(
        id=doc.id,
        provider=doc.provider,
        name=doc.name,
        key_hint=doc.key_suffix,
        created_at=doc.created_at.isoformat() if hasattr(doc.created_at, "isoformat") else str(doc.created_at),
        updated_at=doc.updated_at.isoformat() if hasattr(doc.updated_at, "isoformat") else str(doc.updated_at),
    )


def _get_repo(user_uid: str) -> CredentialRepository:
    db = get_firestore_client()
    return CredentialRepository(db, user_uid)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/keys", status_code=status.HTTP_201_CREATED)
async def create_key(body: CreateKeyRequest, current_user: CurrentUser) -> KeyResponse:
    """Create a new encrypted API key credential."""
    _ensure_encryption_configured()

    if not body.key or len(body.key) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="API key must be at least 8 characters",
        )

    encrypted = encrypt(body.key)
    suffix = mask_key(body.key)
    doc_id = str(uuid.uuid4())

    doc = CredentialDocument(
        provider=body.provider,
        name=body.name,
        encrypted_key=encrypted,
        key_suffix=suffix,
    )

    repo = _get_repo(current_user.uid)
    created = repo.create(doc_id, doc)
    return _to_response(created)


@router.get("/keys")
async def list_keys(current_user: CurrentUser) -> list[KeyResponse]:
    """List all credentials for the authenticated user (masked, never decrypted)."""
    repo = _get_repo(current_user.uid)
    docs = repo.list()
    return [_to_response(doc) for doc in docs]


@router.get("/keys/{key_id}")
async def get_key(key_id: str, current_user: CurrentUser) -> KeyResponse:
    """Get a single credential by ID (masked)."""
    repo = _get_repo(current_user.uid)
    doc = repo.get(key_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
    return _to_response(doc)


@router.put("/keys/{key_id}")
async def update_key(key_id: str, body: UpdateKeyRequest, current_user: CurrentUser) -> KeyResponse:
    """Update a credential's name and/or re-encrypt its key."""
    repo = _get_repo(current_user.uid)
    existing = repo.get(key_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")

    update_data: dict = {}

    if body.name is not None:
        update_data["name"] = body.name

    if body.key is not None:
        _ensure_encryption_configured()
        if len(body.key) < 8:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="API key must be at least 8 characters",
            )
        update_data["encrypted_key"] = encrypt(body.key)
        update_data["key_suffix"] = mask_key(body.key)

    updated = repo.update(key_id, update_data)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")
    return _to_response(updated)


@router.delete("/keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_key(key_id: str, current_user: CurrentUser) -> None:
    """Delete a credential. Overwrites the encrypted blob before removal."""
    repo = _get_repo(current_user.uid)
    existing = repo.get(key_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credential not found")

    # Overwrite the encrypted key before deletion
    repo.update(key_id, {"encrypted_key": ""})
    repo.delete(key_id)
