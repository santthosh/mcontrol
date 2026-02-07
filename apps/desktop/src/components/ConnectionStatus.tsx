import { useEffect, useState } from "react";
import { checkHealth, type HealthResponse } from "../lib/api";

type ConnectionState = "connecting" | "connected" | "disconnected";

export function ConnectionStatus() {
  const [state, setState] = useState<ConnectionState>("connecting");
  const [version, setVersion] = useState<string | null>(null);

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

  return (
    <div className="flex items-center gap-2 text-sm">
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
    </div>
  );
}
