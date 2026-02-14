"""Firebase authentication middleware."""

import os
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.lib.config import get_settings

security = HTTPBearer(auto_error=False)


class AuthUser:
    """Authenticated user information."""

    def __init__(
        self,
        uid: str,
        email: str | None = None,
        display_name: str | None = None,
        avatar_url: str | None = None,
    ) -> None:
        self.uid = uid
        self.email = email
        self.display_name = display_name
        self.avatar_url = avatar_url


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
        emulator_host = os.environ.get("FIREBASE_AUTH_EMULATOR_HOST")
        if emulator_host:
            decoded = await _verify_token_emulator(token, emulator_host)
        else:
            decoded = _verify_token_production(token)

        return AuthUser(
            uid=decoded["uid"],
            email=decoded.get("email"),
            display_name=decoded.get("name"),
            avatar_url=decoded.get("picture"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def _verify_token_production(token: str) -> dict:
    """Verify token using Firebase Admin SDK (production)."""
    from firebase_admin import auth

    from app.lib.firebase import _initialize_app

    _initialize_app()
    decoded = auth.verify_id_token(token)
    return decoded


async def _verify_token_emulator(token: str, emulator_host: str) -> dict:
    """Verify token against Firebase Auth emulator."""
    import httpx

    url = f"http://{emulator_host}/identitytoolkit.googleapis.com/v1/accounts:lookup"
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            json={"idToken": token},
            params={"key": "fake-api-key"},
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        data = resp.json()
        users = data.get("users", [])
        if not users:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        user = users[0]
        return {
            "uid": user["localId"],
            "email": user.get("email"),
            "name": user.get("displayName"),
            "picture": user.get("photoUrl"),
        }


# Dependency for protected routes
CurrentUser = Annotated[AuthUser, Depends(get_current_user)]
