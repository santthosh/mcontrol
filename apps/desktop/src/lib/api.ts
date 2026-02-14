/**
 * API client utilities for communicating with the backend.
 */

import { getValidToken } from "./auth";

// API base URL from environment variable, defaults to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

/**
 * Get the current API URL (for debugging/display).
 */
export function getApiUrl(): string {
  return API_BASE_URL;
}

/**
 * Fetch wrapper that injects the Firebase ID token as a Bearer token.
 * Falls back to unauthenticated request if no token is available.
 */
export async function fetchWithAuth(
  url: string,
  options?: RequestInit
): Promise<Response> {
  const token = await getValidToken();
  const headers = new Headers(options?.headers);
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  return fetch(url, { ...options, headers });
}

export interface HealthResponse {
  status: "ok" | "error";
  version: string;
}

/**
 * Check API health status (unauthenticated).
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }
  return response.json();
}

export interface UserProfile {
  uid: string;
  email: string;
  display_name: string | null;
  avatar_url: string | null;
}

/**
 * Get the currently authenticated user's profile.
 */
export async function getCurrentUser(): Promise<UserProfile> {
  const response = await fetchWithAuth(`${API_BASE_URL}/auth/me`);
  if (!response.ok) {
    throw new Error(`Failed to get user: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Exchange a Google OAuth authorization code for Firebase auth tokens.
 */
export async function exchangeGoogleAuthCode(
  code: string,
  redirectUri: string
): Promise<{
  id_token: string;
  refresh_token: string;
  user: UserProfile;
}> {
  const response = await fetch(`${API_BASE_URL}/auth/google/exchange`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, redirect_uri: redirectUri }),
  });
  if (!response.ok) {
    throw new Error(`Google auth exchange failed: ${response.statusText}`);
  }
  return response.json();
}

// ---------------------------------------------------------------------------
// Credentials (API keys)
// ---------------------------------------------------------------------------

export interface Credential {
  id: string;
  provider: string;
  name: string;
  key_hint: string;
  created_at: string;
  updated_at: string;
}

/**
 * Create a new encrypted API key credential.
 */
export async function createKey(
  provider: string,
  name: string,
  key: string
): Promise<Credential> {
  const response = await fetchWithAuth(`${API_BASE_URL}/keys`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ provider, name, key }),
  });
  if (!response.ok) {
    throw new Error(`Failed to create key: ${response.statusText}`);
  }
  return response.json();
}

/**
 * List all credentials for the authenticated user (masked).
 */
export async function listKeys(): Promise<Credential[]> {
  const response = await fetchWithAuth(`${API_BASE_URL}/keys`);
  if (!response.ok) {
    throw new Error(`Failed to list keys: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get a single credential by ID (masked).
 */
export async function getKey(id: string): Promise<Credential> {
  const response = await fetchWithAuth(`${API_BASE_URL}/keys/${id}`);
  if (!response.ok) {
    throw new Error(`Failed to get key: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Update a credential's name and/or re-encrypt its key.
 */
export async function updateKey(
  id: string,
  data: { name?: string; key?: string }
): Promise<Credential> {
  const response = await fetchWithAuth(`${API_BASE_URL}/keys/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Failed to update key: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Delete a credential.
 */
export async function deleteKey(id: string): Promise<void> {
  const response = await fetchWithAuth(`${API_BASE_URL}/keys/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error(`Failed to delete key: ${response.statusText}`);
  }
}

/**
 * Create a WebSocket connection to the API.
 */
export function createWebSocket(): WebSocket {
  const wsUrl = API_BASE_URL.replace(/^http/, "ws") + "/ws";
  return new WebSocket(wsUrl);
}
