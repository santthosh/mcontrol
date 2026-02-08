"""Authentication routes for Google SSO OAuth flow."""

import os
import secrets
import time
import urllib.parse

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.lib.config import get_settings
from app.lib.firebase import get_firestore_client
from app.middleware.auth import CurrentUser
from app.repositories.user import UserRepository

router = APIRouter(tags=["auth"])

# In-memory OAuth session storage (keyed by session_id, 5-min TTL).
# For production at scale, migrate to Redis.
_auth_sessions: dict[str, dict] = {}


class GoogleAuthStartResponse(BaseModel):
    session_id: str
    auth_url: str


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
# Google OAuth flow
# ---------------------------------------------------------------------------


@router.post("/auth/google/start")
async def start_google_auth() -> GoogleAuthStartResponse:
    """Start the Google OAuth flow. Returns a session_id and the OAuth URL."""
    settings = get_settings()

    if not settings.google_client_id:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")

    session_id = secrets.token_urlsafe(32)
    _auth_sessions[session_id] = {
        "created_at": time.time(),
        "status": "pending",
        "tokens": None,
    }

    redirect_uri = f"{settings.api_base_url}/api/auth/google/callback"
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": session_id,
        "access_type": "offline",
        "prompt": "consent",
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

    return GoogleAuthStartResponse(session_id=session_id, auth_url=auth_url)


@router.get("/auth/google/callback", response_class=HTMLResponse)
async def google_auth_callback(
    code: str = Query(...),
    state: str = Query(...),
) -> HTMLResponse:
    """Google OAuth callback. Exchanges the auth code for Firebase tokens."""
    settings = get_settings()

    session = _auth_sessions.get(state)
    if not session:
        raise HTTPException(status_code=400, detail="Invalid or expired session")

    redirect_uri = f"{settings.api_base_url}/api/auth/google/callback"

    try:
        # Exchange authorization code for Google tokens
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if token_resp.status_code != 200:
                session["status"] = "error"
                raise HTTPException(status_code=400, detail="Token exchange failed")
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

        session["status"] = "complete"
        session["tokens"] = {
            "id_token": firebase_result["idToken"],
            "refresh_token": firebase_result["refreshToken"],
            "user": {
                "uid": user.firebase_uid,
                "email": user.email,
                "display_name": user.display_name,
                "avatar_url": user.avatar_url,
            },
        }
    except HTTPException:
        raise
    except Exception:
        session["status"] = "error"
        raise HTTPException(status_code=500, detail="Authentication failed")

    return HTMLResponse(
        "<html><body style='font-family:system-ui;text-align:center;padding:60px;'>"
        "<h2>Sign-in successful!</h2>"
        "<p>You can close this tab and return to Mission Control.</p>"
        "</body></html>"
    )


@router.get("/auth/google/poll")
async def poll_google_auth(session_id: str = Query(...)) -> dict:
    """Poll for the result of a Google OAuth flow."""
    _cleanup_expired_sessions()

    session = _auth_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    if session["status"] == "pending":
        return {"status": "pending"}

    if session["status"] == "error":
        del _auth_sessions[session_id]
        return {"status": "error", "detail": "Authentication failed"}

    # Complete — return tokens and clean up (one-time retrieval)
    tokens = session["tokens"]
    del _auth_sessions[session_id]
    return {"status": "complete", **tokens}


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


def _cleanup_expired_sessions() -> None:
    """Remove OAuth sessions older than 5 minutes."""
    now = time.time()
    expired = [sid for sid, s in _auth_sessions.items() if now - s["created_at"] > 300]
    for sid in expired:
        del _auth_sessions[sid]
