import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import {
  clearAuth,
  getStoredAuth,
  getValidToken,
  signInWithGoogle,
  type AuthUser,
} from "../lib/auth";
import { AuthContext } from "./auth-types";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<AuthUser | null>(null);
  const refreshTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Schedule a token refresh 5 minutes before expiry
  const scheduleRefresh = useCallback(() => {
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
    }

    const stored = getStoredAuth();
    if (!stored) return;

    const msUntilRefresh = stored.expiresAt - Date.now() - 5 * 60 * 1000;
    const delay = Math.max(msUntilRefresh, 0);

    refreshTimerRef.current = setTimeout(async () => {
      const token = await getValidToken();
      if (token) {
        scheduleRefresh();
      } else {
        setUser(null);
      }
    }, delay);
  }, []);

  // Check for existing session on mount
  useEffect(() => {
    (async () => {
      const stored = getStoredAuth();
      if (stored) {
        const token = await getValidToken();
        if (token) {
          setUser(stored.user);
          scheduleRefresh();
        }
      }
      setIsLoading(false);
    })();

    return () => {
      if (refreshTimerRef.current) {
        clearTimeout(refreshTimerRef.current);
      }
    };
  }, [scheduleRefresh]);

  const signIn = useCallback(async () => {
    const result = await signInWithGoogle();
    setUser(result.user);
    scheduleRefresh();
  }, [scheduleRefresh]);

  const signOut = useCallback(() => {
    clearAuth();
    setUser(null);
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        isLoading,
        isAuthenticated: user !== null,
        user,
        signIn,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
