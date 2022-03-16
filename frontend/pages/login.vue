<template>
  <v-container
    fill-height
    fluid
    class="d-flex justify-center align-center"
    :class="{
      'bg-off-white': !$vuetify.theme.dark,
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

      <v-card-title class="headline justify-center pb-1"> Sign In </v-card-title>
      <v-card-text>
        <v-form @submit.prevent="authenticate()">
          <v-text-field
            v-model="form.email"
            :prepend-inner-icon="$globals.icons.email"
            filled
            rounded
            autofocus
            class="rounded-lg"
            name="login"
            label="Email or Username"
            type="text"
          />
          <v-text-field
            id="password"
            v-model="form.password"
            :prepend-inner-icon="$globals.icons.lock"
            filled
            rounded
            class="rounded-lg"
            name="password"
            label="Password"
            type="password"
          />
          <v-checkbox v-model="form.remember" class="ml-2 mt-n2" label="Remember Me"></v-checkbox>
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
              text: 'Sponsor',
              icon: $globals.icons.heart,
              href: 'https://github.com/sponsors/hay-kot',
            },
            {
              text: 'GitHub',
              icon: $globals.icons.github,
              href: 'https://github.com/hay-kot/mealie',
            },
            {
              text: 'Docs',
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
      {{ $vuetify.theme.dark ? "Light Mode" : "Dark Mode" }}
    </v-btn>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, useContext, computed, reactive } from "@nuxtjs/composition-api";
import { useAppInfo } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { useToggleDarkMode } from "~/composables/use-utils";
export default defineComponent({
  layout: "blank",

  setup() {
    const toggleDark = useToggleDarkMode();

    const { $auth } = useContext();

    const form = reactive({
      email: "",
      password: "",
      remember: false,
    });

    const loggingIn = ref(false);

    const appInfo = useAppInfo();

    const allowSignup = computed(() => appInfo.value?.allowSignup || false);

    async function authenticate() {
      if (form.email.length === 0 || form.password.length === 0) {
        alert.error("Please enter your email and password");
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
        // TODO Check if error is an AxiosError, but isAxiosError is not working right now
        // See https://github.com/nuxt-community/axios-module/issues/550
        // Import $axios from useContext()
        // if ($axios.isAxiosError(error) && error.response?.status === 401) {
        // @ts-ignore - see above
        if (error.response?.status === 401) {
          alert.error("Invalid Credentials");
        } else {
          alert.error("Something Went Wrong!");
        }
      }
      loggingIn.value = false;
    }

    return {
      form,
      loggingIn,
      allowSignup,
      authenticate,
      toggleDark,
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
