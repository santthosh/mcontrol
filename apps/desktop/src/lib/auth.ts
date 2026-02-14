/**
 * Authentication module — handles Google SSO via loopback redirect OAuth (RFC 8252).
 * The desktop app starts a local HTTP server, Google redirects to it with the auth code,
 * and the code is exchanged for Firebase tokens via the API.
 */

import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { open } from "@tauri-apps/plugin-shell";
import { exchangeGoogleAuthCode } from "./api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface AuthUser {
  uid: string;
  email: string;
  displayName: string | null;
  avatarUrl: string | null;
}

export interface StoredAuth {
  idToken: string;
  refreshToken: string;
  expiresAt: number; // Unix ms
  user: AuthUser;
}

// ---------------------------------------------------------------------------
// Storage (localStorage)
// ---------------------------------------------------------------------------

const AUTH_STORAGE_KEY = "mcontrol_auth";

export function getStoredAuth(): StoredAuth | null {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as StoredAuth;
  } catch {
    return null;
  }
}

export function saveAuth(auth: StoredAuth): void {
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(auth));
}

export function clearAuth(): void {
  localStorage.removeItem(AUTH_STORAGE_KEY);
}

// ---------------------------------------------------------------------------
// Token refresh
// ---------------------------------------------------------------------------

/**
 * Refresh a Firebase ID token using the refresh token.
 * Works against the public Google securetoken API (or emulator).
 */
export async function refreshIdToken(refreshToken: string): Promise<{
  idToken: string;
  refreshToken: string;
  expiresIn: number;
}> {
  const emulatorHost = import.meta.env.VITE_FIREBASE_AUTH_EMULATOR_HOST;
  const url = emulatorHost
    ? `http://${emulatorHost}/securetoken.googleapis.com/v1/token`
    : "https://securetoken.googleapis.com/v1/token";

  const resp = await fetch(`${url}?key=fake-api-key`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `grant_type=refresh_token&refresh_token=${encodeURIComponent(refreshToken)}`,
  });

  if (!resp.ok) {
    throw new Error("Token refresh failed");
  }

  const data = await resp.json();
  return {
    idToken: data.id_token,
    refreshToken: data.refresh_token,
    expiresIn: Number(data.expires_in),
  };
}

/**
 * Get a valid ID token, refreshing if the stored one is expired or near-expiry.
 * Returns null if no stored auth exists.
 */
export async function getValidToken(): Promise<string | null> {
  const stored = getStoredAuth();
  if (!stored) return null;

  // Refresh if token expires within 5 minutes
  const bufferMs = 5 * 60 * 1000;
  if (Date.now() + bufferMs >= stored.expiresAt) {
    try {
      const refreshed = await refreshIdToken(stored.refreshToken);
      const updated: StoredAuth = {
        ...stored,
        idToken: refreshed.idToken,
        refreshToken: refreshed.refreshToken,
        expiresAt: Date.now() + refreshed.expiresIn * 1000,
      };
      saveAuth(updated);
      return updated.idToken;
    } catch {
      // Refresh failed — clear auth and force re-login
      clearAuth();
      return null;
    }
  }

  return stored.idToken;
}

// ---------------------------------------------------------------------------
// Google SSO (loopback redirect)
// ---------------------------------------------------------------------------

const OAUTH_TIMEOUT_MS = 5 * 60 * 1000;

/**
 * Start Google SSO flow via loopback redirect:
 * 1. Start a local HTTP listener via Tauri command
 * 2. Build and open Google OAuth URL in system browser
 * 3. Listen for the oauth-callback event with the auth code
 * 4. Exchange the code for Firebase tokens via the API
 */
export async function signInWithGoogle(): Promise<StoredAuth> {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  if (!clientId) {
    throw new Error("Google OAuth not configured (VITE_GOOGLE_CLIENT_ID missing)");
  }

  // Step 1: Start loopback listener — returns the port
  const port = await invoke<number>("start_oauth_listener");
  const redirectUri = `http://127.0.0.1:${port}`;

  // Step 2: Build Google OAuth URL and open in browser
  const params = new URLSearchParams({
    client_id: clientId,
    redirect_uri: redirectUri,
    response_type: "code",
    scope: "openid email profile",
    access_type: "offline",
    prompt: "consent",
  });
  const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?${params.toString()}`;
  await open(authUrl);

  // Step 3: Wait for the oauth-callback event from the Rust listener
  const code = await new Promise<string>((resolve, reject) => {
    const timeout = setTimeout(() => {
      reject(new Error("Sign-in timed out"));
    }, OAUTH_TIMEOUT_MS);

    listen<{ code: string }>("oauth-callback", (event) => {
      clearTimeout(timeout);
      resolve(event.payload.code);
    }).catch((err) => {
      clearTimeout(timeout);
      reject(err);
    });
  });

  // Step 4: Exchange the code for Firebase tokens via the API
  const data = await exchangeGoogleAuthCode(code, redirectUri);

  const auth: StoredAuth = {
    idToken: data.id_token,
    refreshToken: data.refresh_token,
    expiresAt: Date.now() + 3600 * 1000,
    user: {
      uid: data.user.uid,
      email: data.user.email,
      displayName: data.user.display_name,
      avatarUrl: data.user.avatar_url,
    },
  };
  saveAuth(auth);
  return auth;
}
