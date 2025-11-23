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
  getSession: () => Promise<void>;
  setToken: (token: string | null) => void;
}

const authUser = ref<UserOut | null>(null);
const authStatus = ref<"loading" | "authenticated" | "unauthenticated">("loading");

export const useAuthBackend = function (): AuthState {
  const { $axios } = useNuxtApp();
  const router = useRouter();

  const runtimeConfig = useRuntimeConfig();
  const tokenTimeHours = Number(runtimeConfig.public.TOKEN_TIME) || 48;
  const tokenName = runtimeConfig.public.AUTH_TOKEN;
  const tokenCookie = useCookie(tokenName, { maxAge: tokenTimeHours * 60 * 60 });

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

      const { access_token } = response.data;
      setToken(access_token);
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
      authUser.value = null;
      authStatus.value = "unauthenticated";
      await router.push(callbackUrl || "/login");
    }
  }

  async function refresh(): Promise<void> {
    if (!tokenCookie.value) return;

    try {
      const response = await $axios.get("/api/auth/refresh");
      const { access_token } = response.data;
      setToken(access_token);
      await getSession();
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
