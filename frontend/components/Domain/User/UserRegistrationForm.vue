<template>
  <div>
    <v-card-title class="pt-0">
      <v-icon
        size="large"
        class="mr-3"
      >
        {{ $globals.icons.user }}
      </v-icon>
      <span class="headline"> {{ $t("user-registration.account-details") }}</span>
    </v-card-title>
    <v-divider />
    <v-card-text class="mt-2">
      <v-form
        ref="domAccountForm"
        @submit.prevent
      >
        <v-text-field
          v-model="accountDetails.username.value"
          autofocus
          v-bind="inputAttrs"
          :label="$t('user.username')"
          :prepend-icon="$globals.icons.user"
          :rules="[validators.required]"
          :error-messages="usernameErrorMessages"
          @blur="validateUsername"
        />
        <v-text-field
          v-model="accountDetails.fullName.value"
          v-bind="inputAttrs"
          :label="$t('user.full-name')"
          :prepend-icon="$globals.icons.user"
          :rules="[validators.required]"
        />
        <v-text-field
          v-model="accountDetails.email.value"
          v-bind="inputAttrs"
          :prepend-icon="$globals.icons.email"
          :label="$t('user.email')"
          :rules="[validators.required, validators.email]"
          :error-messages="emailErrorMessages"
          @blur="validateEmail"
        />
        <v-text-field
          v-model="credentials.password1.value"
          v-bind="inputAttrs"
          :type="pwFields.inputType.value"
          :append-inner-icon="pwFields.passwordIcon.value"
          :prepend-icon="$globals.icons.lock"
          :label="$t('user.password')"
          :rules="[validators.required, validators.minLength(8), validators.maxLength(258)]"
          @click:append-inner="pwFields.togglePasswordShow"
        />

        <UserPasswordStrength v-model="credentials.password1.value" />

        <v-text-field
          v-model="credentials.password2.value"
          v-bind="inputAttrs"
          :type="pwFields.inputType.value"
          :append-inner-icon="pwFields.passwordIcon.value"
          :prepend-icon="$globals.icons.lock"
          :label="$t('user.confirm-password')"
          :rules="[validators.required, credentials.passwordMatch]"
          @click:append-inner="pwFields.togglePasswordShow"
        />
        <div class="px-2">
          <v-checkbox
            v-model="accountDetails.advancedOptions.value"
            :label="$t('user.enable-advanced-content')"
          />
          <p class="text-caption mt-n4">
            {{ $t("user.enable-advanced-content-description") }}
          </p>
        </div>
      </v-form>
    </v-card-text>
  </div>
</template>

<script lang="ts">
import { useDark } from "@vueuse/core";
import { validators } from "~/composables/use-validators";
import { useUserRegistrationForm } from "~/composables/use-users/user-registration-form";
import { usePasswordField } from "~/composables/use-passwords";
import UserPasswordStrength from "~/components/Domain/User/UserPasswordStrength.vue";

const inputAttrs = {
  validateOnBlur: true,
  class: "pb-1",
  variant: "solo-filled" as any,
};

export default defineNuxtComponent({
  components: { UserPasswordStrength },
  setup() {
    definePageMeta({
      layout: "blank",
    });

    const isDark = useDark();
    const langDialog = ref(false);

    const pwFields = usePasswordField();
    const {
      accountDetails,
      credentials,
      emailErrorMessages,
      usernameErrorMessages,
      validateUsername,
      validateEmail,
      domAccountForm,
    } = useUserRegistrationForm();
    return {
      accountDetails,
      credentials,
      emailErrorMessages,
      inputAttrs,
      isDark,
      langDialog,
      pwFields,
      usernameErrorMessages,
      validators,
      // Validators
      validateUsername,
      validateEmail,
      // Dom Refs
      domAccountForm,
    };
  },
});
</script>

<style lang="css" scoped>
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
  margin-top: 2.5rem;
}

.icon-divider {
  width: 100%;
  margin-bottom: -2.5rem;
}

.icon-avatar {
  border-color: rgba(0, 0, 0, 0.12);
  border: 2px;
}

.bg-off-white {
  background: #f5f8fa;
}

.preferred-width {
  width: 840px;
}
</style>
