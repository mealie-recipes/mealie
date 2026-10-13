<template>
  <AppAuthShell :title="$t('user.sign-in')">
    <template #above>
      <div v-if="isFirstLogin" class="login-first-time">
        <p>
          {{ $t('user.it-looks-like-this-is-your-first-time-logging-in') }}
        </p>
        <p class="login-first-time__credential">
          <strong>{{ $t('user.username') }}:</strong> changeme@example.com
          <AppButtonCopy
            copy-text="changeme@example.com"
            btn-class="h-auto"
          />
        </p>
        <p class="login-first-time__credential">
          <strong>{{ $t('user.password') }}:</strong> MyPassword
          <AppButtonCopy
            copy-text="MyPassword"
            btn-class="h-auto"
          />
        </p>
        <p class="login-first-time__note">
          {{ $t('user.dont-want-to-see-this-anymore-be-sure-to-change-your-email') }}
        </p>
      </div>
    </template>

    <v-form class="login-form" @submit.prevent="authenticate">
      <template v-if="$appInfo.allowPasswordLogin">
        <v-text-field
          id="username"
          v-model="form.email"
          :prepend-inner-icon="$globals.icons.email"
          variant="solo-filled"
          flat
          width="100%"
          autofocus
          autocomplete="username"
          name="username"
          :label="$t('user.email-or-username')"
          type="text"
        />
        <v-text-field
          id="password"
          v-model="form.password"
          :prepend-inner-icon="$globals.icons.lock"
          :append-inner-icon="passwordIcon"
          variant="solo-filled"
          flat
          autocomplete="current-password"
          name="password"
          :label="$t('user.password')"
          :type="inputType"
          @click:append-inner="togglePasswordShow"
        />
        <div class="login-form__row">
          <v-checkbox
            v-model="form.remember"
            hide-details
            density="compact"
            color="primary"
            :label="$t('user.remember-me')"
          />
          <RouterLink to="/forgot-password" class="login-form__link">
            {{ $t("user.reset-password") }}
          </RouterLink>
        </div>
        <v-btn
          :loading="loggingIn"
          :disabled="oidcLoggingIn"
          variant="elevated"
          color="primary"
          type="submit"
          size="large"
          block
        >
          {{ $t("user.login") }}
        </v-btn>
      </template>

      <div
        v-if="$appInfo.enableOidc && $appInfo.allowPasswordLogin"
        class="login-form__or"
      >
        <span>{{ $t("user.or") }}</span>
      </div>
      <v-btn
        v-if="$appInfo.enableOidc"
        :loading="oidcLoggingIn"
        size="large"
        variant="tonal"
        block
        @click="() => oidcAuthenticate()"
      >
        {{ $t("user.login-oidc") }} {{ $appInfo.oidcProviderName }}
      </v-btn>
    </v-form>

    <div class="login-signup">
      <RouterLink
        v-if="$appInfo.allowSignup && $appInfo.allowPasswordLogin"
        to="/register"
        class="login-form__link"
      >
        {{ $t("user.register") }}
      </RouterLink>
      <span v-else>{{ $t("user.invite-only") }}</span>
    </div>

    <template #footer>
      <a
        v-for="link in [
          {
            text: $t('about.sponsor'),
            icon: $globals.icons.heart,
            href: 'https://github.com/sponsors/hay-kot',
          },
          {
            text: $t('about.github'),
            icon: $globals.icons.github,
            href: 'https://github.com/mealie-recipes/mealie',
          },
          {
            text: $t('about.docs'),
            icon: $globals.icons.folderOutline,
            href: 'https://docs.mealie.io/',
          },
        ]"
        :key="link.text"
        :href="link.href"
        target="_blank"
        rel="noopener"
        class="login-footer-link"
      >
        <v-icon size="14">
          {{ link.icon }}
        </v-icon>
        {{ link.text }}
      </a>
    </template>
  </AppAuthShell>
</template>

<script setup lang="ts">
import { useSessionStorage, whenever } from "@vueuse/core";
import AppAuthShell from "~/components/Layout/LayoutParts/AppAuthShell.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { usePasswordField } from "~/composables/use-passwords";
import { alert } from "~/composables/use-toast";
import { useAsyncKey } from "~/composables/use-utils";
import { isSafeRedirectTarget } from "~/lib/validators/redirect";
import type { AppStartupInfo } from "~/lib/api/types/admin";
import { useUserActivityPreferences } from "~/composables/use-users/preferences";

definePageMeta({
  layout: "blank",
});

const router = useRouter();
const route = useRoute();
const i18n = useI18n();
const auth = useMealieAuth();
const { $appInfo, $axios } = useNuxtApp();
const { loggedIn } = useLoggedInState();
const groupSlug = computed(() => auth.user.value?.groupSlug);
const isDemo = ref(false);
const isFirstLogin = ref(false);
const activityPreferences = useUserActivityPreferences();
const { getDefaultActivityRoute } = useDefaultActivity();

// Survives the page reload that happens during OIDC redirect
const pendingShareRedirect = useSessionStorage<string | null>("pwa_share_redirect", null);

useSeoMeta({
  title: i18n.t("user.login"),
});

const form = reactive({
  email: "",
  password: "",
  // Defaults on: this is a self-hosted app people mostly reach from their own devices, and an
  // unticked box now ends the session when the browser closes.
  // Ideally this is off by default, but we've trained users for years to ignore this checkbox,
  // so turning it off would cause a headache for the majority of users.
  // Maybe we can revisit this in the future.
  remember: true,
});

useAsyncData(useAsyncKey(), async () => {
  const data = await $axios.get<AppStartupInfo>("/api/app/about/startup-info");
  isDemo.value = data.data.isDemo;
  isFirstLogin.value = data.data.isFirstLogin;

  if (data.data.isFirstLogin) {
    form.email = "changeme@example.com";
    form.password = "MyPassword";
  }
});

whenever(
  () => loggedIn.value && groupSlug.value,
  () => {
    // First-login setup always takes priority
    if (!isDemo.value && isFirstLogin.value && auth.user.value?.admin) {
      router.push("/admin/setup");
      return;
    }

    // After login, honour a pending PWA share redirect.
    // The redirect param can arrive via the URL query string (password login)
    // or via sessionStorage (OIDC login, where the OIDC provider reload clears
    // the query string).
    const redirectFromQuery = route.query.redirect as string | undefined;
    const redirectTarget = redirectFromQuery ?? pendingShareRedirect.value;
    if (isSafeRedirectTarget(redirectTarget)) {
      pendingShareRedirect.value = null;
      router.push(redirectTarget);
      return;
    }

    const defaultActivityRoute = getDefaultActivityRoute(
      activityPreferences.value.defaultActivity,
      groupSlug.value,
    );
    if (defaultActivityRoute) {
      router.push(defaultActivityRoute);
    }
    else {
      router.push(`/g/${groupSlug.value || ""}`);
    }
  },
  { immediate: true },
);

const loggingIn = ref(false);
const oidcLoggingIn = ref(false);

const { passwordIcon, inputType, togglePasswordShow } = usePasswordField();

whenever(
  () => $appInfo.enableOidc && $appInfo.oidcRedirect && !isCallback() && !isDirectLogin() /* && !auth.check().valid */,
  () => oidcAuthenticate(),
  { immediate: true },
);

onBeforeMount(async () => {
  if (isCallback()) {
    await oidcAuthenticate(true);
  }
});

function isCallback() {
  const params = new URLSearchParams(window.location.search);
  return params.has("code") || params.has("error");
}

function isDirectLogin() {
  const params = new URLSearchParams(window.location.search);
  return params.has("direct") && params.get("direct") === "1";
}

async function oidcAuthenticate(callback = false) {
  if (callback) {
    oidcLoggingIn.value = true;
    try {
      await auth.oauthSignIn();
    }
    catch (error) {
      await router.replace("/login?direct=1");
      alertOnError(error);
    }
    oidcLoggingIn.value = false;
  }
  else {
    // Save any pending PWA share redirect before leaving for the OIDC provider.
    // The OIDC callback reloads the page, which clears the query string, so we
    // persist the target in sessionStorage and restore it after login.
    const redirectTarget = route.query.redirect as string | undefined;
    if (isSafeRedirectTarget(redirectTarget)) {
      pendingShareRedirect.value = redirectTarget;
    }
    navigateTo("/api/auth/oauth", { external: true }); // start the redirect process
  }
}

async function authenticate() {
  if (form.email.length === 0 || form.password.length === 0) {
    alert.error(i18n.t("user.please-enter-your-email-and-password"));
    return;
  }

  loggingIn.value = true;
  const formData = new FormData();
  formData.append("username", form.email);
  formData.append("password", form.password);
  formData.append("remember_me", String(form.remember));

  try {
    await auth.signIn(formData);
  }
  catch (error) {
    console.log(error);
    alertOnError(error);
  }
  loggingIn.value = false;
}

function alertOnError(error: any) {
  // TODO Check if error is an AxiosError, but isAxiosError is not working right now
  // See https://github.com/nuxt-community/axios-module/issues/550
  // Import $axios from useContext()
  // if ($axios.isAxiosError(error) && error.response?.status === 401) {
  if (error.response?.status === 401) {
    alert.error(i18n.t("user.invalid-credentials"));
  }
  else if (error.response?.status === 423) {
    alert.error(i18n.t("user.account-locked-please-try-again-later"));
  }
  else {
    alert.error(i18n.t("events.something-went-wrong"));
  }
}
</script>

<style lang="css" scoped>
/* Fix password manager autofill detection - Vuetify uses opacity:0 during animation */
:deep(.v-field__input) {
  opacity: 1 !important;
}
</style>

<style lang="css" scoped>
.login-form {
  display: flex;
  flex-direction: column;
  margin-top: 22px;
}

.login-form__row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin: -6px 0 16px;
}

.login-form__link {
  font-size: 14px;
  color: rgb(var(--v-theme-primary));
  text-decoration: none;
  white-space: nowrap;
}

.login-form__link:hover {
  text-decoration: underline;
}

.login-form__or {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 18px 0;
  font-size: 13px;
  color: var(--mealie-text-tertiary);
}

.login-form__or::before,
.login-form__or::after {
  content: "";
  flex: 1;
  height: 1px;
  background: var(--mealie-hairline-strong);
}

.login-signup {
  margin-top: 18px;
  text-align: center;
  font-size: 14px;
  color: var(--mealie-text-tertiary);
}

.login-first-time {
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(var(--v-theme-primary), 0.08);
  box-shadow: inset 0 0 0 1px rgba(var(--v-theme-primary), 0.2);
  font-size: 14px;
  line-height: 1.45;
  color: var(--mealie-ink);
}

.login-first-time p + p {
  margin-top: 4px;
}

.login-first-time__credential {
  display: flex;
  align-items: center;
  gap: 6px;
}

.login-first-time__note {
  margin-top: 8px !important;
  color: var(--mealie-text-secondary);
}

.login-footer-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 6px;
  color: var(--mealie-text-tertiary);
  text-decoration: none;
}

.login-footer-link:hover {
  color: var(--mealie-ink);
}
</style>
