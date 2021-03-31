<template>
  <v-card width="500px">
    <v-divider></v-divider>
    <v-app-bar dark color="primary" class="mt-n1 mb-2">
      <v-icon large left v-if="!loading">
        mdi-account
      </v-icon>
      <v-progress-circular
        v-else
        indeterminate
        color="white"
        large
        class="mr-2"
      >
      </v-progress-circular>
      <v-toolbar-title class="headline">{{ $t("user.login") }}</v-toolbar-title>
      <v-spacer></v-spacer>
    </v-app-bar>

    <v-form @submit.prevent="login">
      <v-card-text>
        <v-text-field
          v-if="!options.isLoggingIn"
          v-model="user.name"
          light="light"
          prepend-icon="person"
          :label="$t('general.name')"
        ></v-text-field>
        <v-text-field
          v-model="user.email"
          light="light"
          prepend-icon="mdi-email"
          validate-on-blur
          :label="$t('user.email')"
          type="email"
        ></v-text-field>
        <v-text-field
          v-model="user.password"
          light="light"
          class="mb-2s"
          prepend-icon="mdi-lock"
          :label="$t('user.password')"
          :type="showPassword ? 'text' : 'password'"
          :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append="showPassword = !showPassword"
        ></v-text-field>
        <v-card-actions>
          <v-btn
            v-if="options.isLoggingIn"
            dark
            color="primary"
            block="block"
            type="submit"
            >{{ $t("user.sign-in") }}
          </v-btn>
        </v-card-actions>

        <v-alert v-if="error" outlined class="mt-3 mb-0" type="error">
          {{ $t("user.could-not-validate-credentials") }}
        </v-alert>
      </v-card-text>
    </v-form>
  </v-card>
</template>

<script>
import { api } from "@/api";
export default {
  props: {},
  data() {
    return {
      loading: false,
      error: false,
      showLogin: false,
      showPassword: false,
      user: {
        email: "",
        password: "",
      },
      options: {
        isLoggingIn: true,
      },
    };
  },
  mounted() {
    this.clear();
  },
  methods: {
    clear() {
      this.user = { email: "", password: "" };
    },
    async login() {
      this.loading = true;
      this.error = false;
      let formData = new FormData();
      formData.append("username", this.user.email);
      formData.append("password", this.user.password);
      let key;
      try {
        key = await api.users.login(formData);
      } catch {
        this.error = true;
      }
      if (key.status != 200) {
        this.error = true;
        this.loading = false;
      } else {
        this.clear();
        this.$store.commit("setToken", key.data.access_token);
        this.$emit("logged-in");
      }

      let user = await api.users.self();
      this.$store.commit("setUserData", user);

      this.loading = false;
    },
  },
};
</script>

<style>
</style>