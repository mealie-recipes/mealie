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

/**
 * Checks whether the access token cookie is present in the browser's cookies.
 *
 * @returns `true` if the access token cookie (`mealie.access_token`) exists, `false` otherwise.
 */
function hasCookieToken(): boolean {
  if (typeof document === "undefined") return false;
  return document.cookie
    .split("; ")
    .some((row) => row.startsWith(`${TOKEN_COOKIE}=`));
}

/**
 * Removes the client-side access token cookie used for authentication.
 *
 * This is a no-op when executed outside the browser. In a browser it invalidates the TOKEN_COOKIE by setting it with `Max-Age=0` and `Path=/`. When the page is served over HTTPS the cookie is set with `SameSite=None; Secure`; otherwise it uses `SameSite=Lax`.
 */
function removeCookieToken() {
  if (typeof document === "undefined") return;
  const secure = window.location.protocol === "https:";
  document.cookie = `${TOKEN_COOKIE}=; Path=/; Max-Age=0; SameSite=${
    secure ? "None" : "Lax"
  }; ${secure ? "Secure;" : ""}`;
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

/**
 * Provides authentication state and actions (user, status, signIn, signOut, refresh, oauthSignIn) to descendant components.
 *
 * @param children - The wrapped React nodes that will receive the authentication context
 * @returns A React provider component that supplies authentication state and handlers to its children
 */
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
        await getSession();
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

/**
 * Access the authentication context provided by AuthProvider.
 *
 * @returns The current authentication context value containing `user`, `loggedIn`, `status`, and auth action functions (`signIn`, `signOut`, `refresh`, `oauthSignIn`).
 * @throws {Error} If called outside of an `AuthProvider`.
 */
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}