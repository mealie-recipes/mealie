<template>
  <AppAuthShell :title="$t('user.reset-password')" :subtitle="$t('user.please-enter-password')">
    <v-form ref="form" class="auth-form" @submit.prevent="requestLink()">
      <v-text-field
        v-model="state.email"
        :prepend-inner-icon="$globals.icons.email"
        variant="solo-filled"
        flat
        autofocus
        name="login"
        :label="$t('user.email')"
        type="text"
      />
      <v-text-field
        v-model="state.password"
        variant="solo-filled"
        flat
        :prepend-inner-icon="$globals.icons.lock"
        name="password"
        autocomplete="new-password"
        :label="$t('user.password')"
        type="password"
        :rules="[validators.required]"
      />
      <v-text-field
        v-model="state.passwordConfirm"
        variant="solo-filled"
        flat
        validate-on="blur"
        :prepend-inner-icon="$globals.icons.lock"
        name="password"
        autocomplete="new-password"
        :label="$t('user.confirm-password')"
        type="password"
        :rules="[validators.required, passwordMatch]"
      />
      <v-btn
        :loading="state.loading"
        color="primary"
        :disabled="token === ''"
        type="submit"
        size="large"
        block
      >
        {{ token === "" ? "Token Required" : $t("user.reset-password") }}
      </v-btn>
    </v-form>
    <div class="auth-back">
      <RouterLink to="/login">
        {{ $t("user.login") }}
      </RouterLink>
    </div>
  </AppAuthShell>
</template>

<script setup lang="ts">
import AppAuthShell from "~/components/Layout/LayoutParts/AppAuthShell.vue";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { validators } from "@/composables/use-validators";
import { useRouteQuery } from "~/composables/use-router";
import type { VForm } from "~/types/auto-forms";

definePageMeta({
  layout: "blank",
});

const state = reactive({
  email: "",
  password: "",
  passwordConfirm: "",
  loading: false,
  error: false,
});

const form = ref<VForm | null>(null);

const i18n = useI18n();
const passwordMatch = () => state.password === state.passwordConfirm || i18n.t("user.password-must-match");

// Set page title
useSeoMeta({
  title: i18n.t("user.login"),
});

// ===================
// Token Getter
const token = useRouteQuery("token", "");

// ===================
// API
const api = useUserApi();
async function requestLink() {
  if (!form.value) {
    return;
  };

  const { valid } = await form.value.validate();
  if (!valid) {
    return;
  };

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
    state.error = false;
    alert.success(i18n.t("user.password-updated"));
    await navigateTo("/login");
  }
  else {
    state.error = true;
    alert.error(i18n.t("events.something-went-wrong"));
  }
}
</script>

<style lang="css" scoped>
.auth-form {
  display: flex;
  flex-direction: column;
  margin-top: 22px;
}

.auth-form__hint {
  margin: -4px 0 18px;
  font-size: 14px;
  line-height: 1.45;
  text-align: center;
  color: var(--mealie-text-secondary);
}

.auth-back {
  margin-top: 18px;
  text-align: center;
  font-size: 14px;
}

.auth-back a {
  color: rgb(var(--v-theme-primary));
  text-decoration: none;
}

.auth-back a:hover {
  text-decoration: underline;
}
</style>
