<template>
  <v-card width="500px">
    <v-divider></v-divider>
    <v-app-bar dark color="primary" class="mt-n1">
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
      <v-toolbar-title class="headline"> Sign Up </v-toolbar-title>
      <v-spacer></v-spacer>
    </v-app-bar>
    <v-card-text>
      Welcome to Mealie! To become a user of this instance you are required to
      have a valid invitation link. If you haven't recieved an invitation you
      are unable to sign-up. To recieve a link, contact the sites administrator.
      <v-divider class="mt-3"></v-divider>
      <v-form ref="signUpForm" @submit="signUp">
        <v-text-field
          v-model="user.name"
          light="light"
          prepend-icon="mdi-account"
          validate-on-blur
          :rules="[existsRule]"
          label="Display Name"
          type="email"
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
          :rules="[
            user.password === user.passwordConfirm || 'Password must match',
          ]"
          @click:append="showPassword = !showPassword"
        ></v-text-field>
        <v-card-actions>
          <v-btn
            v-if="options.isLoggingIn"
            @click.prevent="signUp"
            dark
            color="primary"
            block="block"
            type="submit"
          >
            Sign Up
          </v-btn>
        </v-card-actions>
        <v-alert dense v-if="error" outlined class="mt-3 mb-0" type="error">
          Error Signing Up
        </v-alert>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script>
import api from "@/api";
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
        email: this.user.email,
        group: "default",
        password: this.user.password,
        admin: false,
      };

      let successUser = false;
      if (this.$refs.signUpForm.validate()) {
        let response = await api.signUps.createUser(this.token, userData);
        successUser = response.snackbar.text.includes("Created");
      }

      this.$emit("user-created");

      this.loading = false;
      if (successUser) {
        this.$router.push("/");
      }
    },
  },
};
</script>

<style>
</style>