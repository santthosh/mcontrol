"""Credential document model for encrypted API key storage."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, ClassVar

from app.models import BaseDocument


@dataclass
class CredentialDocument(BaseDocument):
    """Credential stored as a subcollection under users/{uid}/credentials."""

    COLLECTION: ClassVar[str] = "credentials"

    provider: str = ""
    name: str = ""
    encrypted_key: str = ""
    key_suffix: str = ""

    # Override base fields with defaults
    id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def from_dict(cls, doc_id: str, data: dict[str, Any]) -> "CredentialDocument":
        """Create CredentialDocument instance from Firestore document data."""
        return cls(
            id=doc_id,
            provider=data.get("provider", ""),
            name=data.get("name", ""),
            encrypted_key=data.get("encrypted_key", ""),
            key_suffix=data.get("key_suffix", ""),
            created_at=data.get("created_at", datetime.now(UTC)),
            updated_at=data.get("updated_at", datetime.now(UTC)),
        )
