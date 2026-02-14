"""Authentication routes for Google SSO via loopback redirect OAuth."""

import os

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.lib.config import get_settings
from app.lib.firebase import get_firestore_client
from app.middleware.auth import CurrentUser
from app.repositories.user import UserRepository

router = APIRouter(tags=["auth"])


class GoogleExchangeRequest(BaseModel):
    code: str
    redirect_uri: str


class UserProfile(BaseModel):
    uid: str
    email: str
    display_name: str | None = None
    avatar_url: str | None = None


class AuthTokenResponse(BaseModel):
    id_token: str
    refresh_token: str
    user: UserProfile


class DevSignInRequest(BaseModel):
    email: str
    display_name: str | None = None


# ---------------------------------------------------------------------------
# Google OAuth — loopback redirect exchange
# ---------------------------------------------------------------------------


@router.post("/auth/google/exchange")
async def exchange_google_auth_code(body: GoogleExchangeRequest) -> AuthTokenResponse:
    """Exchange a Google OAuth authorization code for Firebase auth tokens.

    The desktop app receives the code via a loopback redirect (RFC 8252)
    and sends it here along with the redirect_uri that was used.
    """
    settings = get_settings()

    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    # Exchange authorization code for Google tokens
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": body.code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": body.redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Google token exchange failed: {token_resp.text}",
            )
        google_tokens = token_resp.json()

    # Exchange Google credential for Firebase auth tokens
    firebase_result = await _sign_in_with_google_credential(
        google_tokens["id_token"],
        google_tokens.get("access_token"),
    )

    # Create or update user in Firestore
    db = get_firestore_client()
    user_repo = UserRepository(db)
    user = user_repo.create_or_update(
        firebase_uid=firebase_result["localId"],
        email=firebase_result.get("email", ""),
        display_name=firebase_result.get("displayName"),
        avatar_url=firebase_result.get("photoUrl"),
    )

    return AuthTokenResponse(
        id_token=firebase_result["idToken"],
        refresh_token=firebase_result["refreshToken"],
        user=UserProfile(
            uid=user.firebase_uid,
            email=user.email,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
        ),
    )


# ---------------------------------------------------------------------------
# Dev / emulator sign-in
# ---------------------------------------------------------------------------


@router.post("/auth/dev/signin")
async def dev_sign_in(body: DevSignInRequest) -> AuthTokenResponse:
    """Sign in via Firebase Auth emulator. Only available in emulator mode."""
    emulator_host = os.environ.get("FIREBASE_AUTH_EMULATOR_HOST")
    if not emulator_host:
        raise HTTPException(status_code=404, detail="Not available in production")

    display_name = body.display_name or body.email.split("@")[0]

    async with httpx.AsyncClient() as client:
        # Try sign-up first; fall back to sign-in if user already exists
        signup_resp = await client.post(
            f"http://{emulator_host}/identitytoolkit.googleapis.com/v1/accounts:signUp",
            json={
                "email": body.email,
                "password": "dev-password-123",
                "displayName": display_name,
                "returnSecureToken": True,
            },
            params={"key": "fake-api-key"},
        )

        if signup_resp.status_code == 200:
            data = signup_resp.json()
        else:
            signin_resp = await client.post(
                f"http://{emulator_host}/identitytoolkit.googleapis.com/v1/accounts:signInWithPassword",
                json={
                    "email": body.email,
                    "password": "dev-password-123",
                    "returnSecureToken": True,
                },
                params={"key": "fake-api-key"},
            )
            if signin_resp.status_code != 200:
                raise HTTPException(status_code=400, detail="Emulator auth failed")
            data = signin_resp.json()

    # Create or update user in Firestore
    db = get_firestore_client()
    user_repo = UserRepository(db)
    user = user_repo.create_or_update(
        firebase_uid=data["localId"],
        email=body.email,
        display_name=display_name,
    )

    return AuthTokenResponse(
        id_token=data["idToken"],
        refresh_token=data["refreshToken"],
        user=UserProfile(
            uid=user.firebase_uid,
            email=user.email,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
        ),
    )


# ---------------------------------------------------------------------------
# Authenticated user profile
# ---------------------------------------------------------------------------


@router.get("/auth/me")
async def get_me(current_user: CurrentUser) -> UserProfile:
    """Return the authenticated user's profile from Firestore."""
    db = get_firestore_client()
    user_repo = UserRepository(db)
    db_user = user_repo.get_by_firebase_uid(current_user.uid)

    if db_user:
        return UserProfile(
            uid=db_user.firebase_uid,
            email=db_user.email,
            display_name=db_user.display_name,
            avatar_url=db_user.avatar_url,
        )

    return UserProfile(uid=current_user.uid, email=current_user.email or "")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _sign_in_with_google_credential(
    google_id_token: str,
    access_token: str | None,
) -> dict:
    """Exchange a Google credential for Firebase auth tokens via Identity Toolkit."""
    settings = get_settings()

    emulator_host = os.environ.get("FIREBASE_AUTH_EMULATOR_HOST")
    if emulator_host:
        base_url = f"http://{emulator_host}/identitytoolkit.googleapis.com"
    else:
        base_url = "https://identitytoolkit.googleapis.com"

    post_body = f"id_token={google_id_token}&providerId=google.com"
    if access_token:
        post_body += f"&access_token={access_token}"

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/v1/accounts:signInWithIdp",
            json={
                "postBody": post_body,
                "requestUri": settings.api_base_url,
                "returnIdpCredential": True,
                "returnSecureToken": True,
            },
            params={"key": settings.google_client_id},
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail=f"Firebase signInWithIdp failed: {resp.text}",
            )
        return resp.json()
