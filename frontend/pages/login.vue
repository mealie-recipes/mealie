<template>
  <v-container
    fill-height
    fluid
    class="d-flex justify-center align-center"
    :class="{
      'bg-off-white': !$vuetify.theme.dark && !isDark,
    }"
  >
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

      <v-card-title class="headline justify-center pb-1"> {{ $t('user.sign-in') }} </v-card-title>
      <v-card-text>
        <v-form @submit.prevent="authenticate">
          <v-text-field
            v-model="form.email"
            :prepend-inner-icon="$globals.icons.email"
            filled
            rounded
            autofocus
            class="rounded-lg"
            name="login"
            :label="$t('user.email-or-username')"
            type="text"
          />
          <v-text-field
            id="password"
            v-model="form.password"
            :prepend-inner-icon="$globals.icons.lock"
            :append-icon="passwordIcon"
            filled
            rounded
            class="rounded-lg"
            name="password"
            :label="$t('user.password')"
            :type="inputType"
            @click:append="togglePasswordShow"
          />
          <v-checkbox v-model="form.remember" class="ml-2 mt-n2" :label="$t('user.remember-me')"></v-checkbox>
          <v-card-actions class="justify-center pt-0">
            <div class="max-button">
              <v-btn :loading="loggingIn" color="primary" type="submit" large rounded class="rounded-xl" block>
                {{ $t("user.login") }}
              </v-btn>
            </div>
          </v-card-actions>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-btn v-if="allowSignup" text to="/register"> {{ $t("user.register") }} </v-btn>
        <v-btn v-else text disabled> {{ $t("user.invite-only") }} </v-btn>
        <v-btn class="mr-auto" text to="/forgot-password"> {{ $t("user.reset-password") }} </v-btn>
      </v-card-actions>

      <v-divider></v-divider>

      <v-card-text class="d-flex justify-center">
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

    <v-btn absolute bottom center @click="toggleDark">
      <v-icon left>
        {{ $vuetify.theme.dark ? $globals.icons.weatherSunny : $globals.icons.weatherNight }}
      </v-icon>
      {{ $vuetify.theme.dark ? $t('settings.theme.light-mode') : $t('settings.theme.dark-mode') }}
    </v-btn>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, useContext, computed, reactive, useRouter } from "@nuxtjs/composition-api";
import { useDark, whenever } from "@vueuse/core";
import { useAppInfo } from "~/composables/api";
import { usePasswordField } from "~/composables/use-passwords";
import { alert } from "~/composables/use-toast";
import { useToggleDarkMode } from "~/composables/use-utils";
export default defineComponent({
  layout: "blank",

  setup() {
    const toggleDark = useToggleDarkMode();
    const isDark = useDark();

    const router = useRouter();
    const { $auth, i18n } = useContext();

    whenever(
      () => $auth.loggedIn,
      () => {
        router.push("/");
      },
      { immediate: true },
    );

    const form = reactive({
      email: "",
      password: "",
      remember: false,
    });

    const loggingIn = ref(false);

    const appInfo = useAppInfo();

    const { passwordIcon, inputType, togglePasswordShow } = usePasswordField();

    whenever(
      () => appInfo.value?.jwtAuthEnabled as boolean,
      () => {
        authenticate({sso: true});
      },
      {immediate: true},
    );

    const allowSignup = computed(() => appInfo.value?.allowSignup || false);

    async function authenticate({sso} = {sso: false}) {
      if (!sso) {
        if (form.email.length === 0 || form.password.length === 0) {
          alert.error(i18n.t("user.please-enter-your-email-and-password") as string);
          return;
        }
      }

      loggingIn.value = true;
      const formData = new FormData();
      formData.append("username", sso ? "SSO" : form.email);
      formData.append("password", sso ? "SSO" : form.password);
      formData.append("remember_me", String(form.remember));

      try {
        await $auth.loginWith("local", { data: formData });
      } catch (error) {
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
      loggingIn.value = false;
    }

    return {
      isDark,
      form,
      loggingIn,
      allowSignup,
      authenticate,
      toggleDark,
      passwordIcon,
      inputType,
      togglePasswordShow,
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
</style>
