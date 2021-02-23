<template>
  <div>
    <v-card max-width="500px">
      <v-divider></v-divider>
      <v-app-bar dark color="primary mt-n1">
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
        <v-toolbar-title class="headline"> Login </v-toolbar-title>

        <v-spacer></v-spacer>
      </v-app-bar>

      <v-card-text>
        <v-form>
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
            :label="$t('login.email')"
            type="email"
          ></v-text-field>
          <v-text-field
            v-model="user.password"
            light="light"
            prepend-icon="mdi-lock"
            :label="$t('login.password')"
            :type="showPassword ? 'text' : 'password'"
            :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
            @click:append="showPassword = !showPassword"
          ></v-text-field>
          <v-checkbox
            class="mb-2 mt-0"
            v-if="options.isLoggingIn"
            v-model="options.shouldStayLoggedIn"
            light="light"
            :label="$t('login.stay-logged-in')"
            hide-details="hide-details"
          ></v-checkbox>
          <v-btn
            v-if="options.isLoggingIn"
            @click.prevent="login"
            dark
            color="primary"
            block="block"
            type="submit"
            >{{ $t("login.sign-in") }}</v-btn
          >
          <v-btn
            v-else
            block="block"
            type="submit"
            @click.prevent="options.isLoggingIn = true"
            >{{ $t("login.sign-up") }}</v-btn
          >
        </v-form>
        <v-alert v-if="error" outlined class="mt-3 mb-0" type="error">
          Could Not Validate Credentials
        </v-alert>
      </v-card-text>
      <!-- <v-card-actions v-if="options.isLoggingIn" class="card-actions">
        <div>
          Don't have an account?
        </div>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          light="light"
          @click="options.isLoggingIn = false"
        >
          Sign up
        </v-btn>
      </v-card-actions> -->
    </v-card>
  </div>
</template>

<script>
import api from "@/api";
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
      if (key.status != 200) this.error = true;
      else {
        this.$emit("logged-in");
        this.clear();
      }
      console.log(key);
      this.$store.commit("setToken", key.data.access_token)
      this.loading = false;
    },
  },
};
</script>

<style>
</style>