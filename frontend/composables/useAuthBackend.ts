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
  signOut: () => Promise<void>;
  refresh: () => Promise<void>;
  getSession: () => Promise<void>;
}

// Global auth state
const authUser = ref<UserOut | null>(null);
const authStatus = ref<"loading" | "authenticated" | "unauthenticated">("unauthenticated");

export const useAuthBackend = function (): AuthState {
  const { $axios } = useNuxtApp();
  const router = useRouter();
  const tokenName = useRuntimeConfig().public.AUTH_TOKEN;

  // Token management
  const tokenCookie = useCookie(tokenName, {
    default: () => null as string | null,
    httpOnly: false,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 60 * 60 * 24 * 30, // 30 days
  });

  // Set token helper
  function setToken(token: string | null) {
    tokenCookie.value = token;
  }

  // Get current session/user data
  async function getSession(): Promise<void> {
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
      // Only clear token if it's an auth error (401), not network errors
      if (error?.response?.status === 401) {
        // Token is invalid/expired - clear it
        setToken(null);
        authUser.value = null;
        authStatus.value = "unauthenticated";
      }
      else {
        // Network error or other issue - keep token but set status
        authStatus.value = "unauthenticated";
      }
      throw error;
    }
  }

  // Sign in function
  async function signIn(
    credentials: FormData,
    options: { redirect?: boolean } = { redirect: true },
  ): Promise<void> {
    authStatus.value = "loading";

    try {
      const response = await $axios.post("/api/auth/token", credentials, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const { access_token } = response.data;
      setToken(access_token);

      // Fetch user session after successful login
      await getSession();

      if (options.redirect !== false) {
        await router.push("/");
      }
    }
    catch (error) {
      authStatus.value = "unauthenticated";
      throw error;
    }
  }

  // Sign out function
  async function signOut(): Promise<void> {
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
      await router.push("/login");
    }
  }

  // Refresh token
  async function refresh(): Promise<void> {
    if (!tokenCookie.value) return;

    try {
      const response = await $axios.get("/api/auth/refresh");
      const { access_token } = response.data;
      setToken(access_token);
      await getSession();
    }
    catch (error: any) {
      // Only sign out on auth errors, not network errors
      if (error?.response?.status === 401 || error?.response?.status === 403) {
        await signOut();
      }
      throw error;
    }
  }

  // Auto-refresh user data periodically when authenticated
  if (import.meta.client) {
    let refreshInterval: NodeJS.Timeout | null = null;

    watch(() => authStatus.value, (status) => {
      if (status === "authenticated") {
        // Refresh user data every 5 minutes when authenticated
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

  // Initialize auth state if token exists
  if (import.meta.client && tokenCookie.value && authStatus.value === "unauthenticated") {
    getSession().catch((error: any) => {
      // Only clear token on auth errors, not network errors
      if (error?.response?.status === 401 || error?.response?.status === 403) {
        setToken(null);
      }
      // For network errors, keep the token - user might be offline
    });
  }

  return {
    data: computed(() => authUser.value),
    status: computed(() => authStatus.value),
    signIn,
    signOut,
    refresh,
    getSession,
  };
};

// Custom useAuthState replacement
export const useAuthState = function () {
  const tokenName = useRuntimeConfig().public.AUTH_TOKEN;
  const tokenCookie = useCookie(tokenName);

  function setToken(token: string | null) {
    tokenCookie.value = token;
  }

  return {
    setToken,
  };
};
