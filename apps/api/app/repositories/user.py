"""User repository for Firestore operations."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from google.cloud.firestore_v1 import Client

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User document operations."""

    def __init__(self, db: "Client"):
        """Initialize user repository."""
        super().__init__(db, User)

    def get_by_firebase_uid(self, firebase_uid: str) -> User | None:
        """Get a user by Firebase UID."""
        # Firebase UID is used as document ID
        return self.get(firebase_uid)

    def get_by_email(self, email: str) -> User | None:
        """Get a user by email address."""
        docs = self.collection.where("email", "==", email).limit(1).stream()
        for doc in docs:
            return self._to_model(doc.id, doc.to_dict() or {})
        return None

    def create_or_update(
        self,
        firebase_uid: str,
        email: str,
        display_name: str | None = None,
        avatar_url: str | None = None,
    ) -> User:
        """Create or update a user by Firebase UID."""
        existing = self.get(firebase_uid)
        if existing:
            return (
                self.update(
                    firebase_uid,
                    {
                        "email": email,
                        "display_name": display_name,
                        "avatar_url": avatar_url,
                    },
                )
                or existing
            )
        user = User(
            firebase_uid=firebase_uid,
            email=email,
            display_name=display_name,
            avatar_url=avatar_url,
        )
        return self.create(firebase_uid, user)
