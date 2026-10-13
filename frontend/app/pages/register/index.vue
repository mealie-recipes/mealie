<template>
  <AppAuthShell wide>
    <div class="register">
      <!-- Form Container -->
      <div class="register__step">
        <template v-if="state.ctx.state === States.Initial">
          <div class="register-initial">
            <h1 class="register-initial__title">
              {{ $t("user-registration.user-registration") }}
            </h1>
            <div class="register-choices">
              <button type="button" class="register-choice" @click="initial.joinGroup">
                <span class="register-choice__icon">
                  <v-icon size="22">{{ $globals.icons.group }}</v-icon>
                </span>
                <span class="register-choice__title">{{ $t("user-registration.join-a-group") }}</span>
              </button>
              <button type="button" class="register-choice" @click="initial.createGroup">
                <span class="register-choice__icon">
                  <v-icon size="22">{{ $globals.icons.user }}</v-icon>
                </span>
                <span class="register-choice__title">{{ $t("user-registration.create-a-new-group") }}</span>
              </button>
            </div>
          </div>
        </template>

        <template v-else-if="state.ctx.state === States.ProvideToken">
          <div>
            <v-card-title>
              <v-icon
                size="large"
                class="mr-3"
              >
                {{ $globals.icons.group }}
              </v-icon>
              <span> {{ $t("user-registration.join-a-group") }} </span>
            </v-card-title>
            <v-divider />
            <v-card-text>
              {{ $t("user-registration.provide-registration-token-description") }}
              <v-form
                ref="domTokenForm"
                class="mt-4"
                @submit.prevent
              >
                <v-text-field
                  v-model="token"
                  v-bind="inputAttrs"
                  :label="$t('group.group-token')"
                  :rules="[validators.required]"
                />
              </v-form>
            </v-card-text>
            <v-divider />
            <v-card-actions class="mt-auto justify-space-between">
              <BaseButton
                cancel
                @click="state.back"
              >
                <template #icon>
                  {{ $globals.icons.back }}
                </template>
                {{ $t("general.back") }}
              </BaseButton>
              <BaseButton
                icon-right
                :disabled="!isTokenValid"
                @click="provideToken.next"
              >
                <template #icon>
                  {{ $globals.icons.forward }}
                </template>
                {{ $t("general.next") }}
              </BaseButton>
            </v-card-actions>
          </div>
        </template>

        <template v-else-if="state.ctx.state === States.ProvideGroupDetails">
          <div>
            <v-card-title>
              <v-icon
                size="large"
                class="mr-3"
              >
                {{ $globals.icons.group }}
              </v-icon>
              <span> {{ $t("user-registration.group-details") }}</span>
            </v-card-title>
            <v-card-text>
              {{ $t("user-registration.group-details-description") }}
            </v-card-text>
            <v-divider />
            <v-card-text>
              <v-form
                ref="domGroupForm"
                v-model="isGroupFormValid"
                @submit.prevent
              >
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
                    :label="$t('group.settings.keep-my-recipes-private')"
                  />
                  <p class="text-caption mt-1">
                    {{ $t("group.settings.keep-my-recipes-private-description") }}
                  </p>
                  <v-checkbox
                    v-model="groupDetails.groupSeed.value"
                    hide-details
                    :label="$t('data-pages.seed-data')"
                  />
                  <p class="text-caption mt-1">
                    {{ $t("user-registration.use-seed-data-description") }}
                  </p>
                </div>
              </v-form>
            </v-card-text>
            <v-divider />
            <v-card-actions class="justify-space-between">
              <BaseButton
                cancel
                @click="state.back"
              >
                <template #icon>
                  {{ $globals.icons.back }}
                </template>
                {{ $t("general.back") }}
              </BaseButton>
              <BaseButton
                icon-right
                :disabled="!isGroupFormValid || !groupNameValid"
                @click="groupDetails.next"
              >
                <template #icon>
                  {{ $globals.icons.forward }}
                </template>
                {{ $t("general.next") }}
              </BaseButton>
            </v-card-actions>
          </div>
        </template>

        <template v-else-if="state.ctx.state === States.ProvideAccountDetails">
          <div>
            <UserRegistrationForm v-model="isAccountFormValid" />
            <v-divider />
            <v-card-actions class="justify-space-between">
              <BaseButton
                cancel
                @click="state.back"
              >
                <template #icon>
                  {{ $globals.icons.back }}
                </template>
                {{ $t("general.back") }}
              </BaseButton>
              <BaseButton
                icon-right
                :disabled="!isAccountFormValid"
                @click="accountDetailsNext"
              >
                <template #icon>
                  {{ $globals.icons.forward }}
                </template>
                {{ $t("general.next") }}
              </BaseButton>
            </v-card-actions>
          </div>
        </template>

        <template v-else-if="state.ctx.state === States.Confirmation">
          <div>
            <v-card-title class="mb-0 pb-0">
              <v-icon
                size="large"
                class="mr-3"
              >
                {{ $globals.icons.user }}
              </v-icon>
              <span>{{ $t("general.confirm") }}</span>
            </v-card-title>
            <v-list>
              <template v-for="(item, idx) in confirmationData">
                <v-list-item
                  v-if="item.display"
                  :key="idx"
                >
                  <v-list-item-title> {{ item.text }} </v-list-item-title>
                  <v-list-item-subtitle> {{ item.value }} </v-list-item-subtitle>
                </v-list-item>
                <v-divider
                  v-if="idx !== confirmationData.length - 1"
                  :key="`divider-${idx}`"
                />
              </template>
            </v-list>

            <v-divider />
            <v-card-actions class="justify-space-between">
              <BaseButton
                cancel
                @click="state.back"
              >
                <template #icon>
                  {{ $globals.icons.back }}
                </template>
                {{ $t("general.back") }}
              </BaseButton>
              <BaseButton @click="submitRegistration">
                <template #icon>
                  {{ $globals.icons.check }}
                </template>
                {{ $t("general.submit") }}
              </BaseButton>
            </v-card-actions>
          </div>
        </template>
      </div>
    </div>

    <template #footer>
      <RouterLink to="/login" class="register-footer-link">
        {{ $t("user.login") }}
      </RouterLink>
      <button type="button" class="register-footer-link" @click="langDialog = true">
        <v-icon size="14">
          {{ $globals.icons.translate }}
        </v-icon>
        {{ $t("language-dialog.choose-language") }}
      </button>
    </template>
    <LanguageDialog v-model="langDialog" />
  </AppAuthShell>
</template>

<script setup lang="ts">
import { States, RegistrationType, useRegistration } from "./states";
import { useUserRegistrationForm } from "~/composables/use-users/user-registration-form";
import { useRouteQuery } from "~/composables/use-router";
import { validators, useAsyncValidator } from "~/composables/use-validators";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";
import type { CreateUserRegistration } from "~/lib/api/types/user";
import { usePublicApi } from "~/composables/api/api-client";
import { useLocales } from "~/composables/use-locales";
import UserRegistrationForm from "~/components/Domain/User/UserRegistrationForm.vue";
import AppAuthShell from "~/components/Layout/LayoutParts/AppAuthShell.vue";
import type { VForm } from "~/types/auto-forms";

definePageMeta({
  layout: "blank",
});

const inputAttrs = {
  variant: "filled",
  validateOnBlur: true,
};

const i18n = useI18n();

// Registration Context
const state = useRegistration();

// Handle Token URL / Initialization
const token = useRouteQuery("token");
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

// Provide Token
const domTokenForm = ref<VForm | null>(null);
function validateToken() {
  return Boolean(token.value && token.value.trim());
}
const isTokenValid = computed(() => validateToken());
const provideToken = {
  next: async () => {
    if (!await safeValidate(domTokenForm as Ref<VForm>)) {
      return;
    }
    if (validateToken()) {
      state.setState(States.ProvideAccountDetails);
    }
  },
};

// Provide Group Details
const publicApi = usePublicApi();
const domGroupForm = ref<VForm | null>(null);
const isGroupFormValid = ref(false);
const groupName = ref("");
const groupSeed = ref(false);
const groupPrivate = ref(false);
const groupErrorMessages = ref<string[]>([]);
const { validate: validGroupName, valid: groupNameValid } = useAsyncValidator(
  groupName,
  (v: string) => publicApi.validators.group(v),
  i18n.t("validation.group-name-is-taken"),
  groupErrorMessages,
);
async function validateGroup() {
  if (!groupName.value || !groupName.value.trim()) {
    groupErrorMessages.value = [i18n.t("validation.required")];
    return false;
  }
  groupErrorMessages.value = [];
  await validGroupName();

  if (!groupNameValid.value) {
    return false;
  }

  return true;
}
const groupDetails = {
  groupName,
  groupSeed,
  groupPrivate,
  next: async () => {
    if (!await validateGroup()) {
      return;
    }
    state.setState(States.ProvideAccountDetails);
  },
};

const isAccountFormValid = ref(false);
const {
  accountDetails,
  credentials,
  safeValidate,
} = useUserRegistrationForm();
async function accountDetailsNext() {
  if (!await accountDetails.validate()) {
    return;
  }
  state.setState(States.Confirmation);
}

// Locale
const { locale } = useLocales();
const langDialog = ref(false);

// Confirmation
const confirmationData = computed(() => {
  return [
    {
      display: state.ctx.type === RegistrationType.CreateGroup,
      text: i18n.t("group.group"),
      value: groupName.value,
    },
    {
      display: state.ctx.type === RegistrationType.CreateGroup,
      text: i18n.t("data-pages.seed-data"),
      value: groupSeed.value ? i18n.t("general.yes") : i18n.t("general.no"),
    },
    {
      display: state.ctx.type === RegistrationType.CreateGroup,
      text: i18n.t("group.settings.keep-my-recipes-private"),
      value: groupPrivate.value ? i18n.t("general.yes") : i18n.t("general.no"),
    },
    {
      display: true,
      text: i18n.t("user.email"),
      value: accountDetails.email.value,
    },
    {
      display: true,
      text: i18n.t("user.full-name"),
      value: accountDetails.fullName.value,
    },
    {
      display: true,
      text: i18n.t("user.username"),
      value: accountDetails.username.value,
    },
    {
      display: true,
      text: i18n.t("user.enable-advanced-content"),
      value: accountDetails.advancedOptions.value ? i18n.t("general.yes") : i18n.t("general.no"),
    },
  ];
});

const api = useUserApi();
const router = useRouter();
async function submitRegistration() {
  const payload: CreateUserRegistration = {
    email: accountDetails.email.value,
    username: accountDetails.username.value,
    fullName: accountDetails.fullName.value,
    password: credentials.password1.value,
    passwordConfirm: credentials.password2.value,
    locale: locale.value,
    advanced: accountDetails.advancedOptions.value,
  };
  if (state.ctx.type === RegistrationType.CreateGroup) {
    payload.group = groupName.value;
    payload.private = groupPrivate.value;
    payload.seedData = groupSeed.value;
  }
  else {
    payload.groupToken = token.value;
  }
  const { response, error } = await api.register.register(payload);
  if (response?.status === 201) {
    accountDetails.reset();
    credentials.reset();
    alert.success(i18n.t("user-registration.registration-success"));
    router.push("/login");
  }
  // The Axios interceptor already shows detail.message errors.
  else if (!error?.response?.data?.detail?.message) {
    alert.error(i18n.t("events.something-went-wrong"));
  }
}
</script>

<style lang="css" scoped>
.register__step {
  display: flex;
  justify-content: center;
}

.register__step > * {
  width: 100%;
}

.register-initial {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 4px 0 8px;
}

.register-initial__title {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.02em;
  text-align: center;
}

.register-choices {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  width: 100%;
}

.register-choice {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 22px 16px;
  border: 0;
  border-radius: 18px;
  background: var(--mealie-canvas);
  box-shadow: inset 0 0 0 1px var(--mealie-hairline-strong);
  color: var(--mealie-ink);
  font: inherit;
  cursor: pointer;
  transition:
    box-shadow 0.15s ease,
    background-color 0.15s ease;
}

.register-choice:hover {
  background: rgba(var(--v-theme-primary), 0.06);
  box-shadow: inset 0 0 0 2px rgb(var(--v-theme-primary));
}

.register-choice:focus-visible {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: 2px;
}

.register-choice__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgb(var(--v-theme-primary));
  color: #fff;
}

.register-choice__title {
  font-size: 16px;
  font-weight: 600;
}

.register-footer-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 6px;
  border: 0;
  background: none;
  color: var(--mealie-text-tertiary);
  font: inherit;
  text-decoration: none;
  cursor: pointer;
}

.register-footer-link:hover {
  color: var(--mealie-ink);
}

/* the later steps keep their card titles and dividers, sized to the shell */
.register :deep(.v-card-title) {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.01em;
  white-space: normal;
}

.register :deep(.v-divider) {
  opacity: 0.08;
}

@media (max-width: 600px) {
  .register-choices {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
