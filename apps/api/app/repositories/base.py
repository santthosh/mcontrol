"""Base repository with generic Firestore CRUD operations."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from google.cloud.firestore_v1 import Client

from app.models import BaseDocument


class BaseRepository[T: BaseDocument]:
    """Generic repository for Firestore document operations."""

    def __init__(self, db: "Client", model_class: type[T]):
        """Initialize repository with Firestore client and model class."""
        self.db = db
        self.model_class = model_class
        self.collection = db.collection(model_class.COLLECTION)

    def _to_model(self, doc_id: str, data: dict[str, Any]) -> T:
        """Convert Firestore document data to model instance."""
        return cast(T, self.model_class.from_dict(doc_id, data))

    def create(self, doc_id: str, model: T) -> T:
        """Create a new document."""
        now = datetime.now(UTC)
        model.created_at = now
        model.updated_at = now
        data = model.to_dict()
        self.collection.document(doc_id).set(data)
        model.id = doc_id
        return model

    def get(self, doc_id: str) -> T | None:
        """Get a document by ID."""
        doc = self.collection.document(doc_id).get()  # type: ignore[union-attr]
        if not doc.exists:  # type: ignore[union-attr]
            return None
        return self._to_model(doc.id, doc.to_dict() or {})  # type: ignore[union-attr]

    def update(self, doc_id: str, data: dict[str, Any]) -> T | None:
        """Update a document with partial data."""
        doc_ref = self.collection.document(doc_id)
        doc = doc_ref.get()  # type: ignore[union-attr]
        if not doc.exists:  # type: ignore[union-attr]
            return None
        data["updated_at"] = datetime.now(UTC)
        doc_ref.update(data)
        updated_doc = doc_ref.get()  # type: ignore[union-attr]
        return self._to_model(updated_doc.id, updated_doc.to_dict() or {})  # type: ignore[union-attr]

    def delete(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        doc_ref = self.collection.document(doc_id)
        doc = doc_ref.get()  # type: ignore[union-attr]
        if not doc.exists:  # type: ignore[union-attr]
            return False
        doc_ref.delete()
        return True

    def list(self, limit: int = 100) -> list[T]:
        """List documents in the collection."""
        docs = self.collection.limit(limit).stream()
        return [self._to_model(doc.id, doc.to_dict() or {}) for doc in docs]  # type: ignore[union-attr]
