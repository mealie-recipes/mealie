<template>
  <v-container fill-height fluid class="d-flex justify-center align-center">
    <v-card color="background d-flex flex-column align-center" flat width="600px">
      <v-card-title class="headline justify-center"> Reset Password </v-card-title>
      <BaseDivider />
      <v-card-text>
        <v-form @submit.prevent="requestLink()">
          <v-text-field
            v-model="email"
            :prepend-icon="$globals.icons.email"
            filled
            rounded
            autofocus
            class="rounded-lg"
            name="login"
            :label="$t('user.email')"
            type="text"
          />
          <v-text-field
            v-model="password"
            filled
            rounded
            class="rounded-lg"
            :prepend-icon="$globals.icons.lock"
            name="password"
            label="Password"
            type="password"
            :rules="[validators.required]"
          />
          <v-text-field
            v-model="passwordConfirm"
            filled
            rounded
            validate-on-blur
            class="rounded-lg"
            :prepend-icon="$globals.icons.lock"
            name="password"
            label="Confirm Password"
            type="password"
            :rules="[validators.required, passwordMatch]"
          />
          <p class="text-center">Please enter your new password.</p>
          <v-card-actions class="justify-center">
            <div class="max-button">
              <v-btn
                :loading="loading"
                color="primary"
                :disabled="token === ''"
                type="submit"
                large
                rounded
                class="rounded-xl"
                block
              >
                <v-icon left>
                  {{ $globals.icons.lock }}
                </v-icon>
                {{ token === "" ? "Token Required" : $t("user.reset-password") }}
              </v-btn>
            </div>
          </v-card-actions>
        </v-form>
      </v-card-text>
      <v-btn class="mx-auto" text nuxt to="/login"> {{ $t("user.login") }} </v-btn>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, toRefs, reactive } from "@nuxtjs/composition-api";
import { useApiSingleton } from "~/composables/use-api";
import { alert } from "~/composables/use-toast";
import { validators } from "@/composables/use-validators";
import { useRouteQuery } from "~/composables/use-router";
export default defineComponent({
  layout: "basic",

  setup() {
    const state = reactive({
      email: "",
      password: "",
      passwordConfirm: "",
      loading: false,
      error: false,
    });

    const passwordMatch = () => state.password === state.passwordConfirm || "Passwords do not match";

    // ===================
    // Token Getter
    const token = useRouteQuery("token", "");

    // ===================
    // API
    const api = useApiSingleton();
    async function requestLink() {
      state.loading = true;
      // TODO: Fix Response to send meaningful error
      const { response } = await api.users.resetPassword({
        token: token.value,
        email: state.email,
        password: state.password,
        passwordConfirm: state.passwordConfirm,
      });

      state.loading = false;

      if (response?.status === 200) {
        state.loading = false;
        state.error = false;
        alert.success("Password Reset Successful");
      } else {
        state.loading = false;
        state.error = true;
        alert.error("Something Went Wrong");
      }
    }

    return {
      passwordMatch,
      token,
      requestLink,
      validators,
      ...toRefs(state),
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
</style>