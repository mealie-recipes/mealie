// lib/auth/auth-context.tsx
"use client";

import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
} from "react";
import type { UserOut, CredentialsRequest } from "@/lib/types/user/user";
import { userApi } from "../api/user";
import { authApi } from "../api/auth";

const TOKEN_COOKIE = "mealie.access_token";

// Helper to check if a token exists client-side before attempting requests
function hasCookieToken(): boolean {
  if (typeof document === "undefined") return false;
  return document.cookie
    .split("; ")
    .some((row) => row.startsWith(`${TOKEN_COOKIE}=`));
}

// Helper to manually force clear the cookie on logout
function removeCookieToken() {
  if (typeof document === "undefined") return;
  const secure = window.location.protocol === "https:";
  document.cookie = `${TOKEN_COOKIE}=; Path=/; Max-Age=0; SameSite=None; ${
    secure ? " Secure;" : ""
  }`;
}

interface AuthContextType {
  user: UserOut | null;
  loggedIn: boolean;
  status: "loading" | "authenticated" | "unauthenticated";
  signIn: (credentials: CredentialsRequest) => Promise<void>;
  signOut: (callbackUrl?: string) => Promise<void>;
  refresh: () => Promise<void>;
  oauthSignIn: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserOut | null>(null);
  const [status, setStatus] = useState<
    "loading" | "authenticated" | "unauthenticated"
  >("loading");

  // Helper to sync state when logging out
  const clearSession = useCallback(() => {
    removeCookieToken();
    setUser(null);
    setStatus("unauthenticated");
  }, []);

  const getSession = useCallback(async () => {
    if (!hasCookieToken()) {
      clearSession();
      return;
    }

    setStatus("loading");
    try {
      // baseRequest automatically handles the fetch
      // Middleware handles the Authorization header via cookie
      const userData = await userApi.fetchSelf();

      setUser(userData);
      setStatus("authenticated");
    } catch (error) {
      console.error("Failed to fetch user session:", error);
      clearSession();
    }
  }, [clearSession]);

  const signIn = useCallback(
    async (credentials: CredentialsRequest) => {
      setStatus("loading");
      try {
        await authApi.fetchToken(credentials);
        // await getSession();
      } catch (error) {
        setStatus("unauthenticated");
        throw error;
      }
    },
    [getSession]
  );

  const signOut = useCallback(
    async (callbackUrl: string = "") => {
      try {
        await authApi.logout();
      } catch (error) {
        console.warn("Logout API call failed:", error);
      } finally {
        // Always clear local state/cookies regardless of API success
        clearSession();
        window.location.href = callbackUrl || "/login";
      }
    },
    [clearSession]
  );

  const refresh = useCallback(async () => {
    if (!hasCookieToken()) return;

    try {
      await authApi.fetchAuthRefreshToken();
      // Refresh usually rotates the cookie; getSession confirms validity.
      await getSession();
    } catch (error) {
      console.error("Token refresh failed:", error);
      throw error;
    }
  }, [getSession]);

  const oauthSignIn = useCallback(async () => {
    try {
      const searchParams = window.location.search; // includes ?code=...&state=...
      await authApi.fetchOAuthCallback(searchParams);
      await getSession();
    } catch (error) {
      console.error("OAuth signin failed:", error);
      throw error;
    }
  }, [getSession]);

  // Initialize on mount
  useEffect(() => {
    getSession();
  }, [getSession]);

  return (
    <AuthContext.Provider
      value={{
        user,
        loggedIn: status === "authenticated",
        status,
        signIn,
        signOut,
        refresh,
        oauthSignIn,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
