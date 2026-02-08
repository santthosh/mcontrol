"""Base repository with generic Firestore CRUD operations."""

from datetime import UTC, datetime

from google.cloud.firestore import Client

from app.models import BaseDocument


class BaseRepository[T: BaseDocument]:
    """Generic repository for Firestore document operations."""

    def __init__(self, db: Client, model_class: type[T]):
        """Initialize repository with Firestore client and model class."""
        self.db = db
        self.model_class = model_class
        self.collection = db.collection(model_class.COLLECTION)

    def _to_model(self, doc_id: str, data: dict) -> T:
        """Convert Firestore document data to model instance."""
        return self.model_class.from_dict(doc_id, data)

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
        doc = self.collection.document(doc_id).get()
        if not doc.exists:
            return None
        return self._to_model(doc.id, doc.to_dict() or {})

    def update(self, doc_id: str, data: dict) -> T | None:
        """Update a document with partial data."""
        doc_ref = self.collection.document(doc_id)
        doc = doc_ref.get()
        if not doc.exists:
            return None
        data["updated_at"] = datetime.now(UTC)
        doc_ref.update(data)
        updated_doc = doc_ref.get()
        return self._to_model(updated_doc.id, updated_doc.to_dict() or {})

    def delete(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        doc_ref = self.collection.document(doc_id)
        doc = doc_ref.get()
        if not doc.exists:
            return False
        doc_ref.delete()
        return True

    def list(self, limit: int = 100) -> list[T]:
        """List documents in the collection."""
        docs = self.collection.limit(limit).stream()
        return [self._to_model(doc.id, doc.to_dict() or {}) for doc in docs]
