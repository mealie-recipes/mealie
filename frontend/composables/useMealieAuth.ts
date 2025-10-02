import { ref, watch, computed } from "vue";
import type { UserOut } from "~/lib/api/types/user";

export const useMealieAuth = function () {
  const auth = useAuth();
  const { setToken } = useAuthState();
  const { $axios } = useNuxtApp();

  // User Management
  const lastUser = ref<UserOut | null>(null);
  const user = computed(() => lastUser.value);

  watch(
    () => auth.data.value,
    (val) => {
      if (val) {
        lastUser.value = val as UserOut;
      }
      else {
        lastUser.value = null;
      }
    },
    { immediate: true },
  );

  // Auth Status Management
  const lastAuthStatus = ref<string>(auth.status.value);
  const loggedIn = computed(() => lastAuthStatus.value === "authenticated");

  watch(
    () => auth.status.value,
    (val) => {
      if (val !== "loading") {
        lastAuthStatus.value = val;
      }
    },
    { immediate: true },
  );

  async function oauthSignIn() {
    const params = new URLSearchParams(window.location.search);
    const { data: token } = await $axios.get<{ access_token: string; token_type: "bearer" }>("/api/auth/oauth/callback", { params });
    setToken(token.access_token);
    await auth.getSession();
  }

  return {
    user,
    loggedIn,
    signIn: auth.signIn,
    signOut: auth.signOut,
    signUp: auth.signUp,
    refresh: auth.refresh,
    oauthSignIn,
  };
};
