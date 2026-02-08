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
 * Create a WebSocket connection to the API.
 */
export function createWebSocket(): WebSocket {
  const wsUrl = API_BASE_URL.replace(/^http/, "ws") + "/ws";
  return new WebSocket(wsUrl);
}
