<template>
  <v-container fill-height fluid class="d-flex justify-center align-center">
    <v-card color="background d-flex flex-column align-center" flat width="600px">
      <v-card-title class="headline justify-center"> Forgot Password </v-card-title>
      <BaseDivider />
      <v-card-text>
        <v-form @submit.prevent="requestLink()">
          <v-text-field
            v-model="email"
            filled
            rounded
            autofocus
            class="rounded-lg"
            name="login"
            :label="$t('user.email')"
            type="text"
          />
          <p class="text-center">Please enter your email address and we will send you a link to reset your password.</p>
          <v-card-actions class="justify-center">
            <div class="max-button">
              <v-btn :loading="loading" color="primary" type="submit" large rounded class="rounded-xl" block>
                <v-icon left>
                  {{ $globals.icons.email }}
                </v-icon>
                {{ $t("user.reset-password") }}
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
export default defineComponent({
  layout: "basic",

  setup() {
    const state = reactive({
      email: "",
      loading: false,
      error: false,
    });

    const api = useApiSingleton();

    async function requestLink() {
      state.loading = true;
      // TODO: Fix Response to send meaningful error
      const { response } = await api.email.sendForgotPassword({ email: state.email });

      if (response?.status === 200) {
        state.loading = false;
        state.error = false;
        alert.success("Link successfully sent");
      } else {
        state.loading = false;
        state.error = true;
        alert.error("Email failure");
      }
    }

    return {
      requestLink,
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