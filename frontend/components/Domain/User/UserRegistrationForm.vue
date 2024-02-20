<template>
  <div>
    <v-card-title>
      <v-icon large class="mr-3"> {{ $globals.icons.user }}</v-icon>
      <span class="headline"> {{ $t("user-registration.account-details") }}</span>
    </v-card-title>
    <v-divider />
    <v-card-text>
      <v-form ref="domAccountForm" @submit.prevent>
        <v-text-field
          v-model="accountDetails.username.value"
          autofocus
          v-bind="inputAttrs"
          :label="$tc('user.username')"
          :prepend-icon="$globals.icons.user"
          :rules="[validators.required]"
          :error-messages="usernameErrorMessages"
          @blur="validateUsername"
        />
        <v-text-field
          v-model="accountDetails.fullName.value"
          v-bind="inputAttrs"
          :label="$tc('user.full-name')"
          :prepend-icon="$globals.icons.user"
          :rules="[validators.required]"
        />
        <v-text-field
          v-model="accountDetails.email.value"
          v-bind="inputAttrs"
          :prepend-icon="$globals.icons.email"
          :label="$tc('user.email')"
          :rules="[validators.required, validators.email]"
          :error-messages="emailErrorMessages"
          @blur="validateEmail"
        />
        <v-text-field
          v-model="credentials.password1.value"
          v-bind="inputAttrs"
          :type="pwFields.inputType.value"
          :append-icon="pwFields.passwordIcon.value"
          :prepend-icon="$globals.icons.lock"
          :label="$tc('user.password')"
          :rules="[validators.required, validators.minLength(8), validators.maxLength(258)]"
          @click:append="pwFields.togglePasswordShow"
        />

        <UserPasswordStrength :value="credentials.password1.value" />

        <v-text-field
          v-model="credentials.password2.value"
          v-bind="inputAttrs"
          :type="pwFields.inputType.value"
          :append-icon="pwFields.passwordIcon.value"
          :prepend-icon="$globals.icons.lock"
          :label="$tc('user.confirm-password')"
          :rules="[validators.required, credentials.passwordMatch]"
          @click:append="pwFields.togglePasswordShow"
        />
        <div class="px-2">
          <v-checkbox
            v-model="accountDetails.advancedOptions.value"
            :label="$tc('user.enable-advanced-content')"
          />
          <p class="text-caption mt-n4">
            {{ $tc("user.enable-advanced-content-description") }}
          </p>
        </div>
      </v-form>
    </v-card-text>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from "@nuxtjs/composition-api";
import { useDark } from "@vueuse/core";
import { validators } from "~/composables/use-validators";
import { useUserRegistrationForm } from "~/composables/use-users/user-registration-form";
import { usePasswordField } from "~/composables/use-passwords";
import UserPasswordStrength from "~/components/Domain/User/UserPasswordStrength.vue";

const inputAttrs = {
  filled: true,
  rounded: true,
  validateOnBlur: true,
  class: "rounded-lg",
};

export default defineComponent({
  components: { UserPasswordStrength },
  layout: "blank",
  setup() {
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
