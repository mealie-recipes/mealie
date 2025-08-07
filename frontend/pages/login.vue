<template>
  <v-container
    fluid
    class="d-flex justify-center align-center flex-column fill-height"
    :class="{
      'bg-off-white': !$vuetify.theme.current.dark && !isDark,
    }"
  >
    <v-alert
      v-if="isFirstLogin"
      class="my-4"
      type="info"
      :icon="$globals.icons.information"
      :style="{ flex: 'none' }"
    >
      <div>
        <p class="mb-3">
          {{ $t('user.it-looks-like-this-is-your-first-time-logging-in') }}
        </p>
        <p class="mb-1">
          <strong>{{ $t('user.username') }}:</strong> changeme@example.com
        </p>
        <p class="mb-3">
          <strong>{{ $t('user.password') }}:</strong> MyPassword
        </p>
        <p>
          {{ $t('user.dont-want-to-see-this-anymore-be-sure-to-change-your-email') }}
        </p>
      </div>
    </v-alert>
    <v-card
      tag="section"
      class="d-flex flex-column align-center w-100"
      max-width="600"
    >
      <v-toolbar
        color="primary"
        class="d-flex justify-center mb-4"
        dark
      >
        <v-toolbar-title class="text-h4 text-center">
          Mealie
        </v-toolbar-title>
      </v-toolbar>

      <div class="icon-container">
        <v-divider class="icon-divider" />
        <v-avatar
          class="pa-2 icon-avatar"
          color="primary"
          size="100"
        >
          <svg
            class="icon-white"
            style="width: 100px; height: 100px"
            viewBox="0 0 24 24"
          >
            <path
              d="M8.1,13.34L3.91,9.16C2.35,7.59 2.35,5.06 3.91,3.5L10.93,10.5L8.1,13.34M13.41,13L20.29,19.88L18.88,21.29L12,14.41L5.12,21.29L3.71,19.88L13.36,10.22L13.16,10C12.38,9.23 12.38,7.97 13.16,7.19L17.5,2.82L18.43,3.74L15.19,7L16.15,7.94L19.39,4.69L20.31,5.61L17.06,8.85L18,9.81L21.26,6.56L22.18,7.5L17.81,11.84C17.03,12.62 15.77,12.62 15,11.84L14.78,11.64L13.41,13Z"
            />
          </svg>
        </v-avatar>
      </div>

      <v-card-title class="text-h5 justify-center pb-3">
        {{ $t('user.sign-in') }}
      </v-card-title>
      <v-card-text class="w-100">
        <v-form @submit.prevent="authenticate">
          <v-text-field
            v-if="allowPasswordLogin"
            v-model="form.email"
            :prepend-inner-icon="$globals.icons.email"
            variant="solo-filled"
            flat
            width="100%"
            autofocus
            autocomplete="username"
            name="login"
            :label="$t('user.email-or-username')"
            type="text"
          />
          <v-text-field
            v-if="allowPasswordLogin"
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
          <v-checkbox
            v-if="allowPasswordLogin"
            v-model="form.remember"
            class="ml-2 mt-n2"
            :label="$t('user.remember-me')"
          />
          <v-card-actions v-if="allowPasswordLogin" class="justify-center pt-0">
            <div class="max-button">
              <v-btn
                :loading="loggingIn"
                :disabled="oidcLoggingIn"
                variant="elevated"
                color="primary"
                type="submit"
                size="large"
                rounded
                class="rounded-xl"
                block
              >
                {{ $t("user.login") }}
              </v-btn>
            </div>
          </v-card-actions>

          <div
            v-if="allowOidc && allowPasswordLogin"
            class="d-flex my-4 justify-center align-center"
            width="80%"
          >
            <v-divider class="div-width" />
            <span
              class="absolute px-2"
              :class="{
                'bg-white': !$vuetify.theme.current.dark && !isDark,
                'bg-grey-darken-4': $vuetify.theme.current.dark || isDark,
              }"
            >
              {{ $t("user.or") }}
            </span>
          </div>
          <v-card-actions
            v-if="allowOidc"
            class="justify-center"
          >
            <div class="max-button">
              <v-btn
                :loading="oidcLoggingIn"
                color="primary"
                size="large"
                variant="elevated"
                rounded
                class="rounded-xl"
                block
                @click="() => oidcAuthenticate()"
              >
                {{ $t("user.login-oidc") }} {{ oidcProviderName }}
              </v-btn>
            </div>
          </v-card-actions>
        </v-form>
      </v-card-text>
      <v-card-actions class="d-flex justify-center flex-column flex-sm-row">
        <v-btn
          v-if="allowSignup && allowPasswordLogin"
          variant="text"
          to="/register"
        >
          {{ $t("user.register") }}
        </v-btn>
        <v-btn
          v-else
          variant="text"
          disabled
        >
          {{ $t("user.invite-only") }}
        </v-btn>
        <v-btn
          v-if="allowPasswordLogin"
          class="mr-auto"
          variant="text"
          to="/forgot-password"
        >
          {{ $t("user.reset-password") }}
        </v-btn>
      </v-card-actions>

      <v-card-text class="d-flex justify-center flex-column flex-sm-row">
        <div
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
          class="text-center"
        >
          <v-btn
            variant="text"
            :href="link.href"
            target="_blank"
          >
            <v-icon start>
              {{ link.icon }}
            </v-icon>
            {{ link.text }}
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { useDark, whenever } from "@vueuse/core";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useAppInfo } from "~/composables/api";
import { usePasswordField } from "~/composables/use-passwords";
import { alert } from "~/composables/use-toast";
import { useAsyncKey } from "~/composables/use-utils";
import type { AppStartupInfo } from "~/lib/api/types/admin";

export default defineNuxtComponent({
  setup() {
    definePageMeta({
      layout: "blank",
    });
    const isDark = useDark();

    const router = useRouter();
    const i18n = useI18n();
    const $auth = useMealieAuth();
    const { $axios } = useNuxtApp();
    const { loggedIn } = useLoggedInState();
    const groupSlug = computed(() => $auth.user.value?.groupSlug);
    const isDemo = ref(false);
    const isFirstLogin = ref(false);

    useSeoMeta({
      title: i18n.t("user.login"),
    });

    const form = reactive({
      email: "",
      password: "",
      remember: false,
    });

    useAsyncData(useAsyncKey(), async () => {
      const data = await $axios.get<AppStartupInfo>("/api/app/about/startup-info");
      isDemo.value = data.data.isDemo;
      isFirstLogin.value = data.data.isFirstLogin;
    });

    whenever(
      () => loggedIn.value && groupSlug.value,
      () => {
        if (!isDemo.value && isFirstLogin.value && $auth.user.value?.admin) {
          router.push("/admin/setup");
        }
        else {
          router.push(`/g/${groupSlug.value || ""}`);
        }
      },
      { immediate: true },
    );

    const loggingIn = ref(false);
    const oidcLoggingIn = ref(false);

    const appInfo = useAppInfo();

    const { passwordIcon, inputType, togglePasswordShow } = usePasswordField();

    const allowSignup = computed(() => appInfo.value?.allowSignup || false);
    const allowOidc = computed(() => appInfo.value?.enableOidc || false);
    const oidcRedirect = computed(() => appInfo.value?.oidcRedirect || false);
    const oidcProviderName = computed(() => appInfo.value?.oidcProviderName || "OAuth");
    const allowPasswordLogin = computed(() => appInfo.value?.allowPasswordLogin ?? true);

    whenever(
      () => allowOidc.value && oidcRedirect.value && !isCallback() && !isDirectLogin() /* && !$auth.check().valid */,
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
          await $auth.oauthSignIn();
          window.location.href = "/"; // Reload the app to get the new user
        }
        catch (error) {
          await router.replace("/login?direct=1");
          alertOnError(error);
        }
        oidcLoggingIn.value = false;
      }
      else {
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
        await $auth.signIn(formData, { redirect: false });
        window.location.href = "/"; // Reload the app to get the new user
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

    return {
      isDark,
      form,
      loggingIn,
      allowSignup,
      allowPasswordLogin,
      allowOidc,
      authenticate,
      oidcAuthenticate,
      oidcProviderName,
      oidcLoggingIn,
      passwordIcon,
      inputType,
      togglePasswordShow,
      isFirstLogin,
    };
  },
});
</script>

<style lang="css">
.max-button {
  width: 300px;
}

.icon-white {
  fill: white;
}

.icon-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  position: relative;
  margin-top: 3.5rem;
}

.icon-divider {
  width: 100%;
  margin-bottom: -3.5rem;
}

.icon-avatar {
  border-color: rgba(0, 0, 0, 0.12);
  border: 2px;
}

.bg-off-white {
  background: #f5f8fa;
}

.absolute {
  position: absolute;
}

.div-width {
  max-width: 75%;
}

.bg-white {
  background-color: #fff;
}
</style>
