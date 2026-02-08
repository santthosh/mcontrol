/**
 * API client utilities for communicating with the backend.
 */

// API base URL from environment variable, defaults to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export interface HealthResponse {
  status: "ok" | "error";
  version: string;
}

/**
 * Check API health status.
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
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
