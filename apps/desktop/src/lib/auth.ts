/**
 * Authentication module — handles Google SSO via server-mediated OAuth
 * and dev sign-in via Firebase Auth emulator.
 */

import { open } from "@tauri-apps/plugin-shell";
import { getApiUrl } from "./api";

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
// Environment helpers
// ---------------------------------------------------------------------------

export function isEmulatorMode(): boolean {
  return !!import.meta.env.VITE_FIREBASE_AUTH_EMULATOR_HOST;
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
// Google SSO (server-mediated)
// ---------------------------------------------------------------------------

const POLL_INTERVAL_MS = 1500;
const POLL_TIMEOUT_MS = 5 * 60 * 1000;

/**
 * Start Google SSO flow: calls API to get OAuth URL, opens system browser,
 * polls for completion.
 */
export async function signInWithGoogle(): Promise<StoredAuth> {
  const apiUrl = getApiUrl();

  // Step 1: Start OAuth session
  const startResp = await fetch(`${apiUrl}/auth/google/start`, {
    method: "POST",
  });
  if (!startResp.ok) {
    throw new Error("Failed to start Google sign-in");
  }
  const { session_id, auth_url } = await startResp.json();

  // Step 2: Open system browser
  await open(auth_url);

  // Step 3: Poll for result
  const deadline = Date.now() + POLL_TIMEOUT_MS;
  while (Date.now() < deadline) {
    await sleep(POLL_INTERVAL_MS);

    const pollResp = await fetch(
      `${apiUrl}/auth/google/poll?session_id=${encodeURIComponent(session_id)}`
    );
    if (!pollResp.ok) {
      throw new Error("Polling failed");
    }

    const result = await pollResp.json();

    if (result.status === "complete") {
      const auth: StoredAuth = {
        idToken: result.id_token,
        refreshToken: result.refresh_token,
        // Firebase ID tokens expire after 1 hour
        expiresAt: Date.now() + 3600 * 1000,
        user: {
          uid: result.user.uid,
          email: result.user.email,
          displayName: result.user.display_name,
          avatarUrl: result.user.avatar_url,
        },
      };
      saveAuth(auth);
      return auth;
    }

    if (result.status === "error") {
      throw new Error(result.detail || "Authentication failed");
    }

    // status === "pending" — keep polling
  }

  throw new Error("Sign-in timed out");
}

// ---------------------------------------------------------------------------
// Dev / emulator sign-in
// ---------------------------------------------------------------------------

/**
 * Sign in via the Firebase Auth emulator with just an email address.
 */
export async function signInDev(email: string): Promise<StoredAuth> {
  const apiUrl = getApiUrl();

  const resp = await fetch(`${apiUrl}/auth/dev/signin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  if (!resp.ok) {
    throw new Error("Dev sign-in failed");
  }

  const data = await resp.json();
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

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
