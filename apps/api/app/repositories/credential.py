"""Credential repository for user-scoped Firestore subcollection."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from google.cloud.firestore_v1 import Client

from app.models.credential import CredentialDocument


class CredentialRepository:
    """Repository for credentials stored under users/{uid}/credentials."""

    def __init__(self, db: "Client", user_id: str):
        """Initialize with Firestore client and the owning user's UID."""
        self.db = db
        self.collection = db.collection("users").document(user_id).collection("credentials")

    def _to_model(self, doc_id: str, data: dict[str, Any]) -> CredentialDocument:
        """Convert Firestore document data to model instance."""
        return cast(CredentialDocument, CredentialDocument.from_dict(doc_id, data))

    def create(self, doc_id: str, model: CredentialDocument) -> CredentialDocument:
        """Create a new credential document."""
        now = datetime.now(UTC)
        model.created_at = now
        model.updated_at = now
        data = model.to_dict()
        self.collection.document(doc_id).set(data)
        model.id = doc_id
        return model

    def get(self, doc_id: str) -> CredentialDocument | None:
        """Get a credential by ID."""
        doc = self.collection.document(doc_id).get()  # type: ignore[union-attr]
        if not doc.exists:  # type: ignore[union-attr]
            return None
        return self._to_model(doc.id, doc.to_dict() or {})  # type: ignore[union-attr]

    def list(self, limit: int = 50) -> list[CredentialDocument]:
        """List all credentials for this user."""
        docs = self.collection.limit(limit).stream()
        return [self._to_model(doc.id, doc.to_dict() or {}) for doc in docs]  # type: ignore[union-attr]

    def update(self, doc_id: str, data: dict[str, Any]) -> CredentialDocument | None:
        """Update a credential with partial data."""
        doc_ref = self.collection.document(doc_id)
        doc = doc_ref.get()  # type: ignore[union-attr]
        if not doc.exists:  # type: ignore[union-attr]
            return None
        data["updated_at"] = datetime.now(UTC)
        doc_ref.update(data)
        updated_doc = doc_ref.get()  # type: ignore[union-attr]
        return self._to_model(updated_doc.id, updated_doc.to_dict() or {})  # type: ignore[union-attr]

    def delete(self, doc_id: str) -> bool:
        """Delete a credential by ID."""
        doc_ref = self.collection.document(doc_id)
        doc = doc_ref.get()  # type: ignore[union-attr]
        if not doc.exists:  # type: ignore[union-attr]
            return False
        doc_ref.delete()
        return True
