<template>
  <v-container
    fill-height
    fluid
    class="d-flex justify-center align-center"
    :class="{
      'bg-off-white': !$vuetify.theme.dark && !isDark.value,
    }"
  >
    <LanguageDialog v-model="langDialog" />

    <v-card class="d-flex flex-column" width="1200px" min-height="700px">
      <div>
        <v-toolbar width="100%" color="primary" class="d-flex justify-center" style="margin-bottom: 4rem" dark>
          <v-toolbar-title class="headline text-h4"> Mealie </v-toolbar-title>
        </v-toolbar>

        <div class="icon-container">
          <v-divider class="icon-divider"></v-divider>
          <v-avatar class="pa-2 icon-avatar" color="primary" size="75">
            <svg class="icon-white" style="width: 75" viewBox="0 0 24 24">
              <path
                d="M8.1,13.34L3.91,9.16C2.35,7.59 2.35,5.06 3.91,3.5L10.93,10.5L8.1,13.34M13.41,13L20.29,19.88L18.88,21.29L12,14.41L5.12,21.29L3.71,19.88L13.36,10.22L13.16,10C12.38,9.23 12.38,7.97 13.16,7.19L17.5,2.82L18.43,3.74L15.19,7L16.15,7.94L19.39,4.69L20.31,5.61L17.06,8.85L18,9.81L21.26,6.56L22.18,7.5L17.81,11.84C17.03,12.62 15.77,12.62 15,11.84L14.78,11.64L13.41,13Z"
              />
            </svg>
          </v-avatar>
        </div>
      </div>

      <!-- Form Container -->
      <div class="d-flex justify-center grow items-center my-4">
        <template v-if="state.ctx.state === States.Initial">
          <div width="600px">
            <v-card-title class="headline justify-center my-4 mb-5 pb-0">
              {{ $t("user-registration.user-registration") }}
            </v-card-title>

            <div class="d-flex flex-wrap justify-center flex-md-nowrap pa-4" style="gap: 1em">
              <v-card color="primary" dark hover width="300px" outlined @click="initial.joinGroup">
                <v-card-title class="justify-center">
                  <v-icon large left> {{ $globals.icons.group }}</v-icon>
                  {{ $t("user-registration.join-a-group") }}
                </v-card-title>
              </v-card>
              <v-card color="primary" dark hover width="300px" outlined @click="initial.createGroup">
                <v-card-title class="justify-center">
                  <v-icon large left> {{ $globals.icons.user }}</v-icon>

                  {{ $t("user-registration.create-a-new-group") }}
                </v-card-title>
              </v-card>
            </div>
          </div>
        </template>

        <template v-else-if="state.ctx.state === States.ProvideToken">
          <div>
            <v-card-title>
              <v-icon large class="mr-3"> {{ $globals.icons.group }}</v-icon>
              <span class="headline"> {{ $t("user-registration.join-a-group") }} </span>
            </v-card-title>
            <v-divider />
            <v-card-text>
              {{ $t("user-registration.provide-registration-token-description") }}
              <v-form ref="domTokenForm" class="mt-4" @submit.prevent>
                <v-text-field v-model="token" v-bind="inputAttrs" label="Group Token" :rules="[validators.required]" />
              </v-form>
            </v-card-text>
            <v-divider />
            <v-card-actions class="mt-auto justify-space-between">
              <BaseButton cancel @click="state.back">
                <template #icon> {{ $globals.icons.back }}</template>
                {{ $t("general.back") }}
              </BaseButton>
              <BaseButton icon-right @click="provideToken.next">
                <template #icon> {{ $globals.icons.forward }}</template>
                {{ $t("general.next") }}
              </BaseButton>
            </v-card-actions>
          </div>
        </template>

        <template v-else-if="state.ctx.state === States.ProvideGroupDetails">
          <div class="preferred-width">
            <v-card-title>
              <v-icon large class="mr-3"> {{ $globals.icons.group }}</v-icon>
              <span class="headline"> {{ $t("user-registration.group-details") }}</span>
            </v-card-title>
            <v-card-text>
              {{ $t("user-registration.group-details-description") }}
            </v-card-text>
            <v-divider />
            <v-card-text>
              <v-form ref="domGroupForm" @submit.prevent>
                <v-text-field
                  v-model="groupDetails.groupName.value"
                  v-bind="inputAttrs"
                  :label="$t('group.group-name')"
                  :rules="[validators.required]"
                  :error-messages="groupErrorMessages"
                  @blur="validGroupName"
                />
                <div class="mt-n4 px-2">
                  <v-checkbox
                    v-model="groupDetails.groupPrivate.value"
                    hide-details
                    :label="$tc('group.settings.keep-my-recipes-private')"
                  />
                  <p class="text-caption mt-1">
                    {{ $t("group.settings.keep-my-recipes-private-description") }}
                  </p>
                  <v-checkbox
                    v-model="groupDetails.groupSeed.value"
                    hide-details
                    :label="$tc('data-pages.seed-data')"
                  />
                  <p class="text-caption mt-1">
                    {{ $t("user-registration.use-seed-data-description") }}
                  </p>
                </div>
              </v-form>
            </v-card-text>
            <v-divider />
            <v-card-actions class="justify-space-between">
              <BaseButton cancel @click="state.back">
                <template #icon> {{ $globals.icons.back }}</template>
                {{ $t("general.back") }}
              </BaseButton>
              <BaseButton icon-right @click="groupDetails.next">
                <template #icon> {{ $globals.icons.forward }}</template>
                {{ $t("general.next") }}
              </BaseButton>
            </v-card-actions>
          </div>
        </template>

        <template v-else-if="state.ctx.state === States.ProvideAccountDetails">
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
                <div class="d-flex justify-center pb-6 mt-n1">
                  <div style="width: 500px">
                    <strong> {{ $t("user.password-strength", { strength: pwStrength.strength.value }) }}</strong>
                    <v-progress-linear
                      :value="pwStrength.score.value"
                      class="rounded-lg"
                      :color="pwStrength.color.value"
                      height="15"
                    />
                  </div>
                </div>
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
            <v-divider />
            <v-card-actions class="justify-space-between">
              <BaseButton cancel @click="state.back">
                <template #icon> {{ $globals.icons.back }}</template>
                {{ $t("general.back") }}
              </BaseButton>
              <BaseButton icon-right @click="accountDetails.next">
                <template #icon> {{ $globals.icons.forward }}</template>
                {{ $t("general.next") }}
              </BaseButton>
            </v-card-actions>
          </div>
        </template>

        <template v-else-if="state.ctx.state === States.Confirmation">
          <div class="preferred-width">
            <v-card-title class="mb-0 pb-0">
              <v-icon large class="mr-3"> {{ $globals.icons.user }}</v-icon>
              <span class="headline">{{ $t("general.confirm") }}</span>
            </v-card-title>
            <v-list>
              <template v-for="(item, idx) in confirmationData">
                <v-list-item v-if="item.display" :key="idx">
                  <v-list-item-content>
                    <v-list-item-title> {{ item.text }} </v-list-item-title>
                    <v-list-item-subtitle> {{ item.value }} </v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-divider v-if="idx !== confirmationData.length - 1" :key="`divider-${idx}`" />
              </template>
            </v-list>

            <v-divider />
            <v-card-actions class="justify-space-between">
              <BaseButton cancel @click="state.back">
                <template #icon> {{ $globals.icons.back }}</template>
                {{ $t("general.back") }}
              </BaseButton>
              <BaseButton @click="submitRegistration">
                <template #icon> {{ $globals.icons.check }}</template>
                {{ $t("general.submit") }}
              </BaseButton>
            </v-card-actions>
          </div>
        </template>
      </div>

      <v-card-actions class="justify-center flex-column py-8">
        <v-btn text class="mb-2" to="/login"> Login </v-btn>
        <BaseButton large color="primary" @click="langDialog = true">
          <template #icon> {{ $globals.icons.translate }}</template>
          {{ $t("language-dialog.choose-language") }}
        </BaseButton>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref, useRouter, Ref, useContext, computed } from "@nuxtjs/composition-api";
import { useDark } from "@vueuse/core";
import { States, RegistrationType, useRegistration } from "./states";
import { useRouteQuery } from "~/composables/use-router";
import { validators, useAsyncValidator } from "~/composables/use-validators";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import { CreateUserRegistration } from "~/types/api-types/user";
import { VForm } from "~/types/vuetify";
import { usePasswordField, usePasswordStrength } from "~/composables/use-passwords";
import { usePublicApi } from "~/composables/api/api-client";
import { useLocales } from "~/composables/use-locales";

const inputAttrs = {
  filled: true,
  rounded: true,
  validateOnBlur: true,
  class: "rounded-lg",
};

export default defineComponent({
  layout: "blank",
  setup() {
    const { i18n } = useContext();

    const isDark = useDark();

    function safeValidate(form: Ref<VForm | null>) {
      if (form.value && form.value.validate) {
        return form.value.validate();
      }
      return false;
    }

    // ================================================================
    // Registration Context
    //
    // State is used to manage the registration process states and provide
    // a state machine esq interface to interact with the registration workflow.
    const state = useRegistration();

    // ================================================================
    // Handle Token URL / Initialization
    //

    const token = useRouteQuery("token");

    // TODO: We need to have some way to check to see if the site is in a state
    // Where it needs to be initialized with a user, in that case we'll handle that
    // somewhere...
    function initialUser() {
      return false;
    }

    onMounted(() => {
      if (token.value) {
        state.setState(States.ProvideAccountDetails);
        state.setType(RegistrationType.JoinGroup);
      }

      if (initialUser()) {
        state.setState(States.ProvideGroupDetails);
        state.setType(RegistrationType.InitialGroup);
      }
    });

    // ================================================================
    // Initial

    const initial = {
      createGroup: () => {
        state.setState(States.ProvideGroupDetails);
        state.setType(RegistrationType.CreateGroup);

        if (token.value != null) {
          token.value = null;
        }
      },
      joinGroup: () => {
        state.setState(States.ProvideToken);
        state.setType(RegistrationType.JoinGroup);
      },
    };

    // ================================================================
    // Provide Token

    const domTokenForm = ref<VForm | null>(null);

    function validateToken() {
      return true;
    }

    const provideToken = {
      next: () => {
        if (!safeValidate(domTokenForm as Ref<VForm>)) {
          return;
        }

        if (validateToken()) {
          state.setState(States.ProvideAccountDetails);
        }
      },
    };

    // ================================================================
    // Provide Group Details

    const publicApi = usePublicApi();

    const domGroupForm = ref<VForm | null>(null);

    const groupName = ref("");
    const groupSeed = ref(false);
    const groupPrivate = ref(false);
    const groupErrorMessages = ref<string[]>([]);

    const { validate: validGroupName, valid: groupNameValid } = useAsyncValidator(
      groupName,
      (v: string) => publicApi.validators.group(v),
      i18n.tc("validation.group-name-is-taken"),
      groupErrorMessages
    );

    const groupDetails = {
      groupName,
      groupSeed,
      groupPrivate,
      next: () => {
        if (!safeValidate(domGroupForm as Ref<VForm>) || !groupNameValid.value) {
          return;
        }

        state.setState(States.ProvideAccountDetails);
      },
    };

    // ================================================================
    // Provide Account Details

    const domAccountForm = ref<VForm | null>(null);

    const username = ref("");
    const email = ref("");
    const advancedOptions = ref(false);
    const usernameErrorMessages = ref<string[]>([]);

    const { validate: validateUsername, valid: validUsername } = useAsyncValidator(
      username,
      (v: string) => publicApi.validators.username(v),
      i18n.tc("validation.username-is-taken"),
      usernameErrorMessages
    );

    const emailErrorMessages = ref<string[]>([]);
    const { validate: validateEmail, valid: validEmail } = useAsyncValidator(
      email,
      (v: string) => publicApi.validators.email(v),
      i18n.tc("validation.email-is-taken"),
      emailErrorMessages
    );

    const accountDetails = {
      username,
      email,
      advancedOptions,
      next: () => {
        if (!safeValidate(domAccountForm as Ref<VForm>) || !validUsername.value || !validEmail.value) {
          return;
        }

        state.setState(States.Confirmation);
      },
    };

    // ================================================================
    // Provide Credentials

    const password1 = ref("");
    const password2 = ref("");

    const pwStrength = usePasswordStrength(password1);
    const pwFields = usePasswordField();

    const passwordMatch = () => password1.value === password2.value || i18n.tc("user.password-must-match");

    const credentials = {
      password1,
      password2,
      passwordMatch,
    };

    // ================================================================
    // Locale

    const { locale } = useLocales();
    const langDialog = ref(false);

    // ================================================================
    // Confirmation

    const confirmationData = computed(() => {
      return [
        {
          display: state.ctx.type === RegistrationType.CreateGroup,
          text: i18n.tc("group.group"),
          value: groupName.value,
        },
        {
          display: state.ctx.type === RegistrationType.CreateGroup,
          text: i18n.tc("data-pages.seed-data"),
          value: groupSeed.value ? i18n.tc("general.yes") : i18n.tc("general.no"),
        },
        {
          display: state.ctx.type === RegistrationType.CreateGroup,
          text: i18n.tc("group.settings.keep-my-recipes-private"),
          value: groupPrivate.value ? i18n.tc("general.yes") : i18n.tc("general.no"),
        },
        {
          display: true,
          text: i18n.tc("user.email"),
          value: email.value,
        },
        {
          display: true,
          text: i18n.tc("user.username"),
          value: username.value,
        },
        {
          display: true,
          text: i18n.tc("user.enable-advanced-content"),
          value: advancedOptions.value ? i18n.tc("general.yes") : i18n.tc("general.no"),
        },
      ];
    });

    const api = useUserApi();
    const router = useRouter();

    async function submitRegistration() {
      const payload: CreateUserRegistration = {
        email: email.value,
        username: username.value,
        password: password1.value,
        passwordConfirm: password2.value,
        locale: locale.value,
        seedData: groupSeed.value,
      };

      if (state.ctx.type === RegistrationType.CreateGroup) {
        payload.group = groupName.value;
        payload.advanced = advancedOptions.value;
        payload.private = groupPrivate.value;
      } else {
        payload.groupToken = token.value;
      }

      const { response } = await api.register.register(payload);

      if (response?.status === 201) {
        alert.success("Registration Success");
        router.push("/login");
      }
    }

    return {
      accountDetails,
      confirmationData,
      credentials,
      emailErrorMessages,
      groupDetails,
      groupErrorMessages,
      initial,
      inputAttrs,
      isDark,
      langDialog,
      provideToken,
      pwFields,
      pwStrength,
      RegistrationType,
      state,
      States,
      token,
      usernameErrorMessages,
      validators,
      submitRegistration,

      // Validators
      validGroupName,
      validateUsername,
      validateEmail,

      // Dom Refs
      domAccountForm,
      domGroupForm,
      domTokenForm,
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
