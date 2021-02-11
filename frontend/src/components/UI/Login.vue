<template>
  <div class="text-center">
    <v-btn icon @click="showLogin = true">
      <v-icon>mdi-account</v-icon>
    </v-btn>
    <v-dialog v-model="showLogin" width="500">
      <v-flex class="login-form text-xs-center">
        <v-card>
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
                type="password"
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
                >{{$t('login.sign-in')}}</v-btn
              >
              <v-btn
                v-else
                block="block"
                type="submit"
                @click.prevent="options.isLoggingIn = true"
                >{{$t('login.sign-up')}}</v-btn
              >
            </v-form>
          </v-card-text>
          <!-- <v-card-actions v-if="options.isLoggingIn" class="card-actions">
            Don't have an account?
            <v-btn
              color="primary"
              light="light"
              @click="options.isLoggingIn = false"
            >
              Sign up
            </v-btn>
          </v-card-actions> -->
        </v-card>
      </v-flex>
    </v-dialog>
  </div>
</template>

<script>
import api from "../../api";
export default {
  props: {},
  data() {
    return {
      showLogin: false,
      user: {
        email: "",
        password: "",
      },
      options: {
        isLoggingIn: true,
      },
    };
  },
  methods: {
    async login() {
      let key = await api.login(this.user.email, this.user.password);
    },
  },
};
</script>

<style>
</style>