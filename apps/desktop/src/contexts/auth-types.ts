import { createContext } from "react";
import type { AuthUser } from "../lib/auth";

export interface AuthState {
  isLoading: boolean;
  isAuthenticated: boolean;
  user: AuthUser | null;
  signIn: (email?: string) => Promise<void>;
  signOut: () => void;
}

export const AuthContext = createContext<AuthState | null>(null);
