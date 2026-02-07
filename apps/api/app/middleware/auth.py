"""Firebase authentication middleware."""

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.lib.config import get_settings

security = HTTPBearer(auto_error=False)


class AuthUser:
    """Authenticated user information."""

    def __init__(self, uid: str, email: str | None = None) -> None:
        self.uid = uid
        self.email = email


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> AuthUser:
    """
    Validate Firebase token and return current user.

    When AUTH_DISABLED=true, returns a dev user without validation.
    """
    settings = get_settings()

    # Dev bypass - skip auth validation
    if settings.auth_disabled:
        return AuthUser(uid="dev-user", email="dev@localhost")

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        # In production, validate with Firebase Admin SDK
        # from firebase_admin import auth
        # decoded_token = auth.verify_id_token(token)
        # return AuthUser(uid=decoded_token["uid"], email=decoded_token.get("email"))

        # Placeholder - implement Firebase validation
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Firebase auth not configured. Set AUTH_DISABLED=true for development.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


# Dependency for protected routes
CurrentUser = Annotated[AuthUser, Depends(get_current_user)]
