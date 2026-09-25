import axios from "axios";
import type { InternalAxiosRequestConfig } from "axios";
import { alert } from "~/composables/use-toast";
import { readTokenCookie } from "~/composables/use-token-cookie";
import { isSafeRedirectTarget } from "~/lib/validators/redirect";

declare module "axios" {
  interface AxiosRequestConfig {
    suppressAlert?: boolean;
  }
}

/** Requests that must never trigger a refresh, or a failed login would retry itself forever. */
const NO_REFRESH_PATHS = ["/api/auth/token", "/api/auth/refresh", "/api/auth/logout"];

type RetriableConfig = InternalAxiosRequestConfig & { _retriedAfterRefresh?: boolean };

function getErrorDetailMessage(detail: unknown): string | null {
  if (typeof detail === "string") {
    return detail;
  }

  if (detail && typeof detail === "object" && "message" in detail && typeof detail.message === "string") {
    return detail.message;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map(item => item && typeof item === "object" && "msg" in item ? item.msg : null)
      .filter((message): message is string => typeof message === "string");

    return [...new Set(messages)].join("; ") || null;
  }

  return null;
}

export default defineNuxtPlugin((nuxtApp) => {
  const tokenName = useRuntimeConfig().public.AUTH_TOKEN;
  const axiosInstance = axios.create({
    // timeout removed to allow backend to handle timeouts
    baseURL: "/", // api calls already pass with /api
    withCredentials: true,
  });

  axiosInstance.interceptors.request.use(
    (config) => {
      const token = readTokenCookie(tokenName);
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      // The server writes the session cookie now, but can't tell it's being framed — and an embedded
      // deployment needs SameSite=None and a partitioned cookie. So the client flags it.
      if (window.self !== window.top) {
        config.headers["X-Mealie-Embedded"] = "true";
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    },
  );

  function logOutAndRedirect() {
    // Disable beforeunload warnings to prevent "Are you sure you want to leave?" popups
    window.onbeforeunload = null;

    const target = window.location.pathname + window.location.search;
    const redirect = isSafeRedirectTarget(target) && target !== "/login" ? `?redirect=${encodeURIComponent(target)}` : "";
    window.location.href = `/login${redirect}`;
  }

  // Add response interceptor
  axiosInstance.interceptors.response.use(
    (response) => {
      if (response?.data?.message && !response.config?.suppressAlert) alert.info(response.data.message as string);
      return response;
    },
    async (error) => {
      const config = error?.config as RetriableConfig | undefined;

      // A 401 usually just means the token aged out mid-session. Trade it for a fresh one and replay
      // the request, so an expiry doesn't interrupt whatever the user was in the middle of. Only one
      // attempt per request, and concurrent 401s share a single refresh.
      if (
        error?.response?.status === 401
        && config
        && !config._retriedAfterRefresh
        && !NO_REFRESH_PATHS.some(path => config.url?.startsWith(path))
        && readTokenCookie(tokenName)
      ) {
        config._retriedAfterRefresh = true;

        let refreshed = true;
        try {
          await nuxtApp.runWithContext(() => useAuthBackend().refresh());
        }
        catch {
          // Refresh failed, so the session really is over. Fall through to the logout path.
          refreshed = false;
        }

        if (refreshed) {
          try {
            return await axiosInstance(config);
          }
          catch (retryError: any) {
            // The replay carried a good token, so anything other than a second 401 is the request's
            // own problem — a 500, a dropped connection — and has to surface as itself. Treating it
            // as a dead session would log the user out over an unrelated server error.
            if (retryError?.response?.status !== 401) {
              return Promise.reject(retryError);
            }
          }
        }
      }

      const errorMessage = getErrorDetailMessage(error?.response?.data?.detail);
      if (errorMessage) {
        alert.error(errorMessage);
      }

      // A 401 from the logout call itself only means the token was already dead — expired, or
      // invalidated by a password change. We're on our way out regardless, so let signOut finish with
      // its own SPA redirect instead of reloading the page over it. The reload would also wipe any
      // toast the preceding request raised, which is how "password updated" used to vanish.
      const isLoggingOut = config?.url?.startsWith("/api/auth/logout") ?? false;

      // If we receive a 401 Unauthorized response, clear the token cookie and redirect to login
      if (error?.response?.status === 401 && !isLoggingOut) {
        // If tokenCookie is not set, we may just be an unauthenticated user using the wrong API, so don't redirect
        if (readTokenCookie(tokenName)) {
          nuxtApp.runWithContext(() => useAuthBackend().setToken(null));
          logOutAndRedirect();
        }
      }

      return Promise.reject(error);
    },
  );

  return {
    provide: {
      axios: axiosInstance,
    },
  };
});
