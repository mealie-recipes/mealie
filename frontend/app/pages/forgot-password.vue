<template>
  <AppAuthShell :title="$t('user.forgot-password')">
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
        :rules="[validators.email]"
      />
      <p class="auth-form__hint">
        {{ $t('user.forgot-password-text') }}
      </p>
      <v-btn
        :loading="state.loading"
        color="primary"
        type="submit"
        size="large"
        block
      >
        {{ $t("user.reset-password") }}
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
import { validators } from "~/composables/use-validators";
import type { VForm } from "~/types/auto-forms";

definePageMeta({
  layout: "blank",
});

const form = ref<VForm | null>(null);

const state = reactive({
  email: "",
  loading: false,
  error: false,
});

const i18n = useI18n();

// Set page title
useSeoMeta({
  title: i18n.t("user.login"),
});

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
  const { response } = await api.email.sendForgotPassword({ email: state.email });

  state.loading = false;

  if (response?.status === 200) {
    state.error = false;
    alert.success(i18n.t("profile.email-sent"));
    await navigateTo("/login");
  }
  else {
    state.error = true;
    alert.error(i18n.t("profile.error-sending-email"));
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
