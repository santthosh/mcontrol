import { useEffect, useState } from "react";
import { checkHealth, getApiUrl, type HealthResponse } from "../lib/api";

type ConnectionState = "connecting" | "connected" | "disconnected";

export function ConnectionStatus() {
  const [state, setState] = useState<ConnectionState>("connecting");
  const [version, setVersion] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    let mounted = true;

    const pollHealth = async () => {
      try {
        const response: HealthResponse = await checkHealth();
        if (mounted) {
          setState(response.status === "ok" ? "connected" : "disconnected");
          setVersion(response.version);
        }
      } catch {
        if (mounted) {
          setState("disconnected");
          setVersion(null);
        }
      }
    };

    // Initial check
    pollHealth();

    // Poll every 5 seconds
    const interval = setInterval(pollHealth, 5000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const statusColors: Record<ConnectionState, string> = {
    connecting: "bg-yellow-400",
    connected: "bg-green-500",
    disconnected: "bg-red-500",
  };

  const statusLabels: Record<ConnectionState, string> = {
    connecting: "Connecting...",
    connected: "Connected",
    disconnected: "Disconnected",
  };

  const apiUrl = getApiUrl();

  return (
    <div className="relative">
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="flex items-center gap-2 text-sm hover:bg-gray-100 rounded px-2 py-1 transition-colors"
        title="Click for connection details"
      >
        <div
          className={`h-2.5 w-2.5 rounded-full ${statusColors[state]}`}
          aria-hidden="true"
        />
        <span className="text-gray-600">
          {statusLabels[state]}
          {version && state === "connected" && (
            <span className="text-gray-400 ml-1">v{version}</span>
          )}
        </span>
      </button>

      {showDetails && (
        <div className="absolute top-full left-0 mt-1 p-3 bg-white border border-gray-200 rounded-lg shadow-lg z-50 min-w-64">
          <div className="text-xs font-medium text-gray-500 uppercase mb-2">
            Connection Details
          </div>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Status:</span>
              <span className="font-medium">{statusLabels[state]}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">API URL:</span>
              <span className="font-mono text-xs">{apiUrl}</span>
            </div>
            {version && (
              <div className="flex justify-between">
                <span className="text-gray-500">Version:</span>
                <span className="font-medium">{version}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
