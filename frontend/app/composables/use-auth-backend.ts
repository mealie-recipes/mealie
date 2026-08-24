import { ref, computed, watch } from "vue";
import type { UserOut } from "~/lib/api/types/user";
import { clearAllStores } from "~/composables/store";
import { clearComposableCaches } from "~/composables/use-clear-composable-caches";
import { getTokenCookieOptions, getTokenExpiry, isRememberedSession, nextRefreshDelay, readTokenCookie } from "~/composables/use-token-cookie";

interface AuthData {
  value: UserOut | null;
}

interface AuthStatus {
  value: "loading" | "authenticated" | "unauthenticated";
}

interface AuthState {
  data: AuthData;
  status: AuthStatus;
  token: { readonly value: string | null | undefined };
  signIn: (credentials: FormData, options?: { redirect?: boolean }) => Promise<void>;
  signOut: (callbackUrl?: string) => Promise<void>;
  refresh: () => Promise<void>;
  getSession: () => Promise<void>;
  setToken: (token: string | null, expiresInSeconds?: number) => void;
  /** Hydrates the token from the cookie and starts the refresh loop. Called once, by the auth plugin. */
  initTokenRefresh: () => void;
}

/** Retry a refresh that failed for reasons other than auth (offline, server hiccup). */
const REFRESH_RETRY_DELAY_MS = 60_000;

const authUser = ref<UserOut | null>(null);
const authStatus = ref<"loading" | "authenticated" | "unauthenticated">("loading");

// The cookie persists the token; this ref is the reactive view of it. Keeping a plain ref as the
// source of truth means writes are visible synchronously, which the cookie ref can't guarantee — it
// propagates between tabs over a BroadcastChannel, and those messages arrive a tick later.
const accessToken = ref<string | null>(null);

let refreshTimer: ReturnType<typeof setTimeout> | null = null;
let refreshInFlight: Promise<void> | null = null;

export function resetAuth() {
  authUser.value = null;
  authStatus.value = "unauthenticated";
}

export const useAuthBackend = function (): AuthState {
  const { $axios } = useNuxtApp();
  const router = useRouter();

  const runtimeConfig = useRuntimeConfig();
  const tokenName = runtimeConfig.public.AUTH_TOKEN;

  function clearScheduledRefresh() {
    if (refreshTimer) {
      clearTimeout(refreshTimer);
      refreshTimer = null;
    }
  }

  /**
   * Queues the next refresh from the token's own expiry.
   *
   * Recomputing from the remaining time (rather than a fixed interval) means this self-corrects
   * after the machine sleeps or the tab is backgrounded and the timer fires late.
   */
  function scheduleTokenRefresh(token: string | null) {
    clearScheduledRefresh();
    if (!token) {
      return;
    }

    const expiresAt = getTokenExpiry(token);
    if (expiresAt === null) {
      return;
    }

    const delay = nextRefreshDelay(expiresAt - Date.now());
    if (delay === null) {
      return;
    }

    refreshTimer = setTimeout(() => {
      refreshTimer = null;
      void refreshQuietly();
    }, delay);
  }

  function setToken(token: string | null, expiresInSeconds?: number) {
    if (!token) {
      accessToken.value = null;
      clearScheduledRefresh();
      useCookie(tokenName, getTokenCookieOptions()).value = null;
      return;
    }

    // "Remember me" decides whether the cookie outlives the browser session, not how long the token
    // is valid — every session is TOKEN_TIME. Without it we write a session cookie, so closing the
    // browser ends the session as the unticked checkbox promises.
    const expiresAt = getTokenExpiry(token);
    const maxAge = isRememberedSession(token)
      ? (expiresInSeconds ?? (expiresAt === null ? undefined : Math.max(Math.round((expiresAt - Date.now()) / 1000), 1)))
      : undefined;

    accessToken.value = token;

    // A fresh ref each time, because the cookie's max-age has to match this particular token's
    // lifetime and `useCookie` fixes its options when the ref is created.
    useCookie(tokenName, getTokenCookieOptions(maxAge)).value = token;

    scheduleTokenRefresh(token);
  }

  function handleAuthError(error: any, redirect = false) {
    // Only clear token on auth errors, not network errors
    if (error?.response?.status === 401) {
      setToken(null);
      resetAuth();
      if (redirect) {
        router.push("/login");
      }
    }
  }

  async function getSession(): Promise<void> {
    if (!accessToken.value) {
      authUser.value = null;
      authStatus.value = "unauthenticated";
      return;
    }

    authStatus.value = "loading";
    try {
      const { data } = await $axios.get<UserOut>("/api/users/self");
      authUser.value = data;
      authStatus.value = "authenticated";
    }
    catch (error: any) {
      console.error("Failed to fetch user session:", error);
      handleAuthError(error);
      authStatus.value = "unauthenticated";
    }
  }

  async function signIn(credentials: FormData): Promise<void> {
    authStatus.value = "loading";

    try {
      const response = await $axios.post("/api/auth/token", credentials, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const { access_token, expires_in } = response.data;
      setToken(access_token, expires_in);
      await getSession();
    }
    catch (error) {
      authStatus.value = "unauthenticated";
      throw error;
    }
  }

  async function signOut(callbackUrl: string = ""): Promise<void> {
    try {
      await $axios.post("/api/auth/logout");
    }
    catch (error) {
      // Continue with logout even if API call fails
      console.warn("Logout API call failed:", error);
    }
    finally {
      setToken(null);
      resetAuth();

      // Clear all cached store data to prevent data leakage between users
      clearAllStores();

      // Clear cached composable refs to prevent data leakage between users
      clearComposableCaches();

      // Clear Nuxt's useAsyncData cache
      clearNuxtData();

      await router.push(callbackUrl || "/login");
    }
  }

  /**
   * Trades the current token for a fresh one.
   *
   * Concurrent callers share a single request — a page load can easily fire several 401s at once,
   * and each one retrying separately would stampede the endpoint and race over the cookie.
   */
  async function refresh(): Promise<void> {
    if (!accessToken.value) return;
    if (refreshInFlight) return refreshInFlight;

    refreshInFlight = (async () => {
      try {
        const response = await $axios.post("/api/auth/refresh", null, { suppressAlert: true });
        const { access_token, expires_in } = response.data;
        setToken(access_token, expires_in);
        await getSession();
      }
      catch (error: any) {
        handleAuthError(error, true);
        throw error;
      }
      finally {
        refreshInFlight = null;
      }
    })();

    return refreshInFlight;
  }

  /** A background refresh, where there is no caller to surface a failure to. */
  async function refreshQuietly(): Promise<void> {
    try {
      await refresh();
    }
    catch (error: any) {
      // A 401 has already cleared the session and redirected. Anything else — offline, a restarting
      // backend — is transient, so try again rather than letting the session lapse over a blip.
      if (error?.response?.status !== 401 && accessToken.value) {
        clearScheduledRefresh();
        refreshTimer = setTimeout(() => {
          refreshTimer = null;
          void refreshQuietly();
        }, REFRESH_RETRY_DELAY_MS);
      }
    }
  }

  /**
   * Starts keeping the session alive. Called once, from the auth plugin.
   *
   * Timers alone aren't enough: they don't run while the device sleeps, and a laptop reopened after
   * a day would otherwise come back to an expired token. Re-scheduling on focus, visibility and
   * reconnect recomputes the delay against the real clock without costing a request.
   */
  function initTokenRefresh() {
    accessToken.value = readTokenCookie(tokenName);

    // Read-only, and deliberately without a max-age: a ref carrying one starts an expiry timer that
    // clears the cookie when it elapses, which would cut a 14-day remembered session down to
    // TOKEN_TIME. This ref exists only to observe, never to write.
    const tokenCookie = useCookie<string | null>(tokenName, { readonly: true });

    // Nuxt syncs cookie refs between tabs, so this also picks up a refresh performed elsewhere and
    // re-schedules against the new expiry instead of duplicating the work.
    watch(tokenCookie, (value) => {
      if (value && value !== accessToken.value) {
        accessToken.value = value;
        scheduleTokenRefresh(value);
      }
    });

    const reschedule = () => scheduleTokenRefresh(accessToken.value);

    window.addEventListener("focus", reschedule);
    window.addEventListener("online", reschedule);
    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible") {
        reschedule();
      }
    });

    scheduleTokenRefresh(accessToken.value);
  }

  return {
    data: computed(() => authUser.value),
    status: computed(() => authStatus.value),
    token: computed(() => accessToken.value),
    signIn,
    signOut,
    refresh,
    getSession,
    setToken,
    initTokenRefresh,
  };
};
