"""User document model."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, ClassVar

from app.models import BaseDocument


@dataclass
class User(BaseDocument):
    """User account document model."""

    COLLECTION: ClassVar[str] = "users"

    firebase_uid: str = ""
    email: str = ""
    display_name: str | None = None
    avatar_url: str | None = None

    # Override base fields with defaults
    id: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def from_dict(cls, doc_id: str, data: dict[str, Any]) -> "User":
        """Create User instance from Firestore document data."""
        return cls(
            id=doc_id,
            firebase_uid=data.get("firebase_uid", ""),
            email=data.get("email", ""),
            display_name=data.get("display_name"),
            avatar_url=data.get("avatar_url"),
            created_at=data.get("created_at", datetime.now(UTC)),
            updated_at=data.get("updated_at", datetime.now(UTC)),
        )

    def __repr__(self) -> str:
        return f"<User {self.email}>"
