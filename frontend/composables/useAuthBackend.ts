import { ref, computed } from "vue";
import type { UserOut } from "~/lib/api/types/user";

interface AuthData {
  value: UserOut | null;
}

interface AuthStatus {
  value: "loading" | "authenticated" | "unauthenticated";
}

interface AuthState {
  data: AuthData;
  status: AuthStatus;
  signIn: (credentials: FormData, options?: { redirect?: boolean }) => Promise<void>;
  signOut: (callbackUrl?: string) => Promise<void>;
  refresh: () => Promise<void>;
  /**
   * Fetches the current user session from the backend using the auth token cookie.
   * @param forceRefreshCookie Whether to refresh the auth token cookie before fetching the session
   * @returns A promise that resolves when the session has been fetched
   */
  getSession: (forceRefreshCookie?: boolean) => Promise<void>;
  setToken: (token: string | null) => void;
}

const authUser = ref<UserOut | null>(null);
const authStatus = ref<"loading" | "authenticated" | "unauthenticated">("loading");

export const useAuthBackend = function (): AuthState {
  const { $axios } = useNuxtApp();
  const router = useRouter();
  const tokenName = useRuntimeConfig().public.AUTH_TOKEN;
  const tokenCookie = useCookie(tokenName);

  function setToken(token: string | null) {
    tokenCookie.value = token;
  }

  function handleAuthError(error: any, redirect = false) {
    // Only clear token on auth errors, not network errors
    if (error?.response?.status === 401) {
      setToken(null);
      authUser.value = null;
      authStatus.value = "unauthenticated";
      if (redirect) {
        router.push("/login");
      }
    }
  }

  /**
   * Waits for the auth token cookie to be set by the backend.
   * The browser should do this immedaitely, but sometimes there is a slight delay, so we poll for it.
   */
  async function waitForCookie(timeoutMs: number = 2000): Promise<void> {
    const startTime = Date.now();

    while (!tokenCookie.value && Date.now() - startTime < timeoutMs) {
      refreshCookie(tokenName);
      if (tokenCookie.value) return;
      await new Promise(resolve => setTimeout(resolve, 50));
    }

    if (!tokenCookie.value) {
      console.warn("Cookie was not set by backend within timeout");
    }
  }

  async function getSession(forceRefreshCookie: boolean = false): Promise<void> {
    if (forceRefreshCookie) {
      await waitForCookie();
    }

    if (!tokenCookie.value) {
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
      await $axios.post("/api/auth/token", credentials, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      await getSession(true);
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
      authUser.value = null;
      authStatus.value = "unauthenticated";
      await router.push(callbackUrl || "/login");
    }
  }

  async function refresh(): Promise<void> {
    if (!tokenCookie.value) return;

    try {
      await $axios.get("/api/auth/refresh");
      await getSession(true);
    }
    catch (error: any) {
      handleAuthError(error, true);
      throw error;
    }
  }

  // Auto-refresh user data periodically when authenticated
  if (import.meta.client) {
    let refreshInterval: NodeJS.Timeout | null = null;

    watch(() => authStatus.value, (status) => {
      if (status === "authenticated") {
        refreshInterval = setInterval(() => {
          if (tokenCookie.value) {
            getSession().catch(() => {
              // Ignore errors in background refresh
            });
          }
        }, 5 * 60 * 1000); // 5 minutes
      }
      else {
        // Clear interval when not authenticated
        if (refreshInterval) {
          clearInterval(refreshInterval);
          refreshInterval = null;
        }
      }
    }, { immediate: true });
  }

  return {
    data: computed(() => authUser.value),
    status: computed(() => authStatus.value),
    signIn,
    signOut,
    refresh,
    getSession,
    setToken,
  };
};
