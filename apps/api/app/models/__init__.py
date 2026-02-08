"""Firestore document models."""

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, ClassVar


@dataclass
class BaseDocument:
    """Base class for all Firestore document models."""

    COLLECTION: ClassVar[str] = ""

    id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary for Firestore storage."""
        data = asdict(self)
        # Remove id from dict (it's the document ID, not a field)
        data.pop("id", None)
        return data

    @classmethod
    def from_dict(cls, doc_id: str, data: dict[str, Any]) -> "BaseDocument":
        """Create model instance from Firestore document data."""
        data["id"] = doc_id
        return cls(**data)
