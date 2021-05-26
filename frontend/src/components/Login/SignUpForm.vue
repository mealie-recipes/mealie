<template>
  <v-card width="500px">
    <v-divider></v-divider>
    <v-app-bar dark color="primary" class="mt-n1">
      <v-icon large left v-if="!loading">
        {{ $globals.icons.user }}
      </v-icon>
      <v-progress-circular v-else indeterminate color="white" large class="mr-2"> </v-progress-circular>
      <v-toolbar-title class="headline">
        {{ $t("signup.sign-up") }}
      </v-toolbar-title>
      <v-spacer></v-spacer>
    </v-app-bar>
    <v-card-text>
      {{ $t("signup.welcome-to-mealie") }}
      <v-divider class="mt-3"></v-divider>
      <v-form ref="signUpForm" @submit.prevent="signUp">
        <v-text-field
          v-model="user.name"
          light="light"
          :prepend-icon="$globals.icons.user"
          validate-on-blur
          :rules="[existsRule]"
          :label="$t('user.full-name')"
        ></v-text-field>
        <v-text-field
          v-model="user.username"
          light="light"
          :prepend-icon="$globals.icons.user"
          validate-on-blur
          :rules="[existsRule]"
          :label="$t('user.username')"
        ></v-text-field>
        <v-text-field
          v-model="user.email"
          light="light"
          prepend-icon="mdi-email"
          validate-on-blur
          :rules="[existsRule, emailRule]"
          :label="$t('user.email')"
          type="email"
        ></v-text-field>
        <v-text-field
          v-model="user.password"
          light="light"
          class="mb-2s"
          prepend-icon="mdi-lock"
          validate-on-blur
          :label="$t('user.password')"
          :type="showPassword ? 'text' : 'password'"
          :rules="[minRule]"
        ></v-text-field>
        <v-text-field
          v-model="user.passwordConfirm"
          light="light"
          class="mb-2s"
          prepend-icon="mdi-lock"
          :label="$t('user.password')"
          :type="showPassword ? 'text' : 'password'"
          :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
          :rules="[user.password === user.passwordConfirm || $t('user.password-must-match')]"
          @click:append="showPassword = !showPassword"
        ></v-text-field>
        <v-card-actions>
          <v-btn v-if="options.isLoggingIn" dark color="primary" block="block" type="submit">
            {{ $t("signup.sign-up") }}
          </v-btn>
        </v-card-actions>
        <v-alert dense v-if="error" outlined class="mt-3 mb-0" type="error">
          {{ $t("signup.error-signing-up") }}
        </v-alert>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script>
import { api } from "@/api";
import { validators } from "@/mixins/validators";
export default {
  mixins: [validators],
  data() {
    return {
      loading: false,
      error: false,
      showPassword: false,
      user: {
        name: "",
        email: "",
        password: "",
        passwordConfirm: "",
      },
      options: {
        isLoggingIn: true,
      },
    };
  },
  mounted() {
    this.clear();
  },
  computed: {
    token() {
      return this.$route.params.token;
    },
  },
  methods: {
    clear() {
      this.user = {
        name: "",
        email: "",
        password: "",
        passwordConfirm: "",
      };
    },
    async signUp() {
      this.loading = true;
      this.error = false;

      const userData = {
        fullName: this.user.name,
        username: this.user.username,
        email: this.user.email,
        group: "default",
        password: this.user.password,
        admin: false,
      };

      if (this.$refs.signUpForm.validate()) {
        if (await api.signUps.createUser(this.token, userData)) {
          this.$emit("user-created");
          this.$router.push("/");
        }
      }

      this.loading = false;
    },
  },
};
</script>

<style></style>
