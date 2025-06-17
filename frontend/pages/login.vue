<template>
  <v-container
    fill-height
    fluid
    class="d-flex justify-center align-center flex-column"
    :class="{
      'bg-off-white': !$vuetify.theme.dark && !isDark,
    }"
  >
    <v-alert v-if="isFirstLogin" class="my-4" type="info" icon="mdi-information">
      <div>
        <p class="mb-3">
          {{ $tc('user.it-looks-like-this-is-your-first-time-logging-in')}}
        </p>
        <p class="mb-1"><strong>{{ $tc('user.username') }}:</strong> changeme@example.com</p>
        <p class="mb-3"><strong>{{  $tc('user.password') }}:</strong> MyPassword</p>
        <p>
          {{  $tc('user.dont-want-to-see-this-anymore-be-sure-to-change-your-email') }}
        </p>
      </div>
    </v-alert>
    <v-card tag="section" class="d-flex flex-column align-center" width="600px">
      <v-toolbar width="100%" color="primary" class="d-flex justify-center mb-4" dark>
        <v-toolbar-title class="headline text-h4"> Mealie </v-toolbar-title>
      </v-toolbar>

      <div class="icon-container">
        <v-divider class="icon-divider"></v-divider>
        <v-avatar class="pa-2 icon-avatar" color="primary" size="100">
          <svg class="icon-white" style="width: 100px; height: 100px" viewBox="0 0 24 24">
            <path
              d="M8.1,13.34L3.91,9.16C2.35,7.59 2.35,5.06 3.91,3.5L10.93,10.5L8.1,13.34M13.41,13L20.29,19.88L18.88,21.29L12,14.41L5.12,21.29L3.71,19.88L13.36,10.22L13.16,10C12.38,9.23 12.38,7.97 13.16,7.19L17.5,2.82L18.43,3.74L15.19,7L16.15,7.94L19.39,4.69L20.31,5.61L17.06,8.85L18,9.81L21.26,6.56L22.18,7.5L17.81,11.84C17.03,12.62 15.77,12.62 15,11.84L14.78,11.64L13.41,13Z"
            />
          </svg>
        </v-avatar>
      </div>

      <v-card-title class="headline justify-center pb-3"> {{ $t('user.sign-in') }} </v-card-title>
      <v-card-text>
        <v-form @submit.prevent="authenticate">
          <v-text-field
            v-if="allowPasswordLogin"
            v-model="form.email"
            :prepend-inner-icon="$globals.icons.email"
            filled
            rounded
            autofocus
            autocomplete="username"
            class="rounded-lg"
            name="login"
            :label="$t('user.email-or-username')"
            type="text"
          />
          <v-text-field
            v-if="allowPasswordLogin"
            id="password"
            v-model="form.password"
            :prepend-inner-icon="$globals.icons.lock"
            :append-icon="passwordIcon"
            filled
            rounded
            autocomplete="current-password"
            class="rounded-lg"
            name="password"
            :label="$t('user.password')"
            :type="inputType"
            @click:append="togglePasswordShow"
          />
          <v-checkbox v-if="allowPasswordLogin" v-model="form.remember" class="ml-2 mt-n2" :label="$t('user.remember-me')"></v-checkbox>
          <v-card-actions v-if="allowPasswordLogin" class="justify-center pt-0">
            <div class="max-button">
              <v-btn :loading="loggingIn" :disabled="oidcLoggingIn" color="primary" type="submit" large rounded class="rounded-xl" block>
                {{ $t("user.login") }}
              </v-btn>
            </div>
          </v-card-actions>

          <div v-if="allowOidc && allowPasswordLogin" class="d-flex my-4 justify-center align-center" width="80%">
            <v-divider class="div-width"/>
            <span
                class="absolute px-2"
                :class="{
                    'bg-white': !$vuetify.theme.dark && !isDark,
                    'bg-background': $vuetify.theme.dark || isDark,
                }"
            >
                {{ $t("user.or") }}
            </span>
          </div>
          <v-card-actions v-if="allowOidc" class="justify-center">
          <div class="max-button">
            <v-btn :loading="oidcLoggingIn" color="primary" large rounded class="rounded-xl" block @click.native="() => oidcAuthenticate()">
                {{ $t("user.login-oidc") }} {{ oidcProviderName }}
            </v-btn>
          </div>
        </v-card-actions>
        </v-form>
      </v-card-text>
      <v-card-actions class="d-flex justify-center flex-column flex-sm-row">
        <v-btn v-if="allowSignup && allowPasswordLogin" text to="/register"> {{ $t("user.register") }} </v-btn>
        <v-btn v-else text disabled> {{ $t("user.invite-only") }} </v-btn>
        <v-btn v-if="allowPasswordLogin" class="mr-auto" text to="/forgot-password"> {{ $t("user.reset-password") }} </v-btn>
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
              href: 'https://github.com/hay-kot/mealie',
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
          <v-btn text :href="link.href" target="_blank">
            <v-icon left>
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
import { defineComponent, ref, useContext, computed, reactive, useRouter, useAsync, onBeforeMount } from "@nuxtjs/composition-api";
import { useDark, whenever } from "@vueuse/core";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { useAppInfo } from "~/composables/api";
import { usePasswordField } from "~/composables/use-passwords";
import { alert } from "~/composables/use-toast";
import { useAsyncKey } from "~/composables/use-utils";
import { AppStartupInfo } from "~/lib/api/types/admin";

export default defineComponent({
  layout: "blank",

  setup() {
    const isDark = useDark();

    const router = useRouter();
    const { $auth, i18n, $axios } = useContext();
    const { loggedIn } = useLoggedInState();
    const groupSlug = computed(() => $auth.user?.groupSlug);
    const isDemo = ref(false);
    const isFirstLogin = ref(false);

    const form = reactive({
      email: "",
      password: "",
      remember: false,
    });

    useAsync(async () => {
      const data = await $axios.get<AppStartupInfo>("/api/app/about/startup-info");
      isDemo.value = data.data.isDemo;
      isFirstLogin.value = data.data.isFirstLogin;
    }, useAsyncKey());

    whenever(
      () => loggedIn.value && groupSlug.value,
      () => {
        if (!isDemo.value && isFirstLogin.value && $auth.user?.admin) {
          router.push("/admin/setup");
        } else {
          router.push(`/g/${groupSlug.value || ""}`);
        }
      },
      { immediate: true },
    );

    const loggingIn = ref(false);
    const oidcLoggingIn = ref(false)

    const appInfo = useAppInfo();

    const { passwordIcon, inputType, togglePasswordShow } = usePasswordField();

    const allowSignup = computed(() => appInfo.value?.allowSignup || false);
    const allowOidc = computed(() => appInfo.value?.enableOidc || false);
    const oidcRedirect = computed(() => appInfo.value?.oidcRedirect || false);
    const oidcProviderName = computed(() => appInfo.value?.oidcProviderName || "OAuth");
    const allowPasswordLogin = computed(() => appInfo.value?.allowPasswordLogin ?? true);


    whenever(
        () => allowOidc.value && oidcRedirect.value && !isCallback() && !isDirectLogin() && !$auth.check().valid,
        () => oidcAuthenticate(),
        {immediate: true}
    )

    onBeforeMount(async () => {
        if (isCallback()) {
            await oidcAuthenticate(true)
        }
    })

    function isCallback() {
        const params = new URLSearchParams(window.location.search)
        return params.has("code") || params.has("error")
    }

    function isDirectLogin() {
        const params = new URLSearchParams(window.location.search)
        return params.has("direct") && params.get("direct") === "1"
    }

    async function oidcAuthenticate(callback = false) {
        if (callback) {
            oidcLoggingIn.value = true
            try {
                await $auth.loginWith("oidc", { params: new URLSearchParams(window.location.search)})
            } catch (error) {
                await router.replace("/login?direct=1")
                alertOnError(error)
            }
            oidcLoggingIn.value = false
        } else {
            window.location.replace("/api/auth/oauth") // start the redirect process
        }
    }

    async function authenticate() {
      if (form.email.length === 0 || form.password.length === 0) {
        alert.error(i18n.t("user.please-enter-your-email-and-password") as string);
        return;
      }

      loggingIn.value = true;
      const formData = new FormData();
      formData.append("username", form.email);
      formData.append("password", form.password);
      formData.append("remember_me", String(form.remember));

      try {
        await $auth.loginWith("local", { data: formData });
      } catch (error) {
        alertOnError(error)
      }
      loggingIn.value = false;
    }

    function alertOnError(error: any) {
        // TODO Check if error is an AxiosError, but isAxiosError is not working right now
        // See https://github.com/nuxt-community/axios-module/issues/550
        // Import $axios from useContext()
        // if ($axios.isAxiosError(error) && error.response?.status === 401) {
        // @ts-ignore- see above
        if (error.response?.status === 401) {
          alert.error(i18n.t("user.invalid-credentials") as string);
          // @ts-ignore - see above
        } else if (error.response?.status === 423) {
          alert.error(i18n.t("user.account-locked-please-try-again-later") as string);
        } else {
          alert.error(i18n.t("events.something-went-wrong") as string);
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
      isFirstLogin
    };
  },

  head() {
    return {
      title: this.$t("user.login") as string,
    };
  },
});
</script>

<style lang="css">
.max-button {
  width: 300px;
}

.icon-primary {
  fill: var(--v-primary-base);
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

.bg-background {
    background-color: #1e1e1e;
}

.bg-white {
    background-color: #fff;
}
</style>
