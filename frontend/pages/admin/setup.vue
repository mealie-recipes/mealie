<template>
  <v-container
    fluid
    class="d-flex justify-center  align-start  fill-height"
    :class="{
      'bg-off-white': !$vuetify.theme.current.dark && !isDark,
    }"
  >
    <!-- Header Toolbar -->
    <v-card class="elevation-4" width="1200" :class="{ 'my-10': $vuetify.display.mdAndUp }">
      <v-toolbar
        color="primary"
        class="d-flex justify-center"
        dark
      >
        <v-toolbar-title class="headline text-h4 text-center mx-0">
          Mealie
        </v-toolbar-title>
      </v-toolbar>

      <!-- Stepper Wizard -->
      <v-stepper v-model="currentPage" mobile-breakpoint="sm">
        <v-stepper-header>
          <v-stepper-item
            :value="Pages.LANDING"
            :complete="currentPage > Pages.LANDING"
            :title="$t('general.start')"
          />
          <v-divider />
          <v-stepper-item
            :value="Pages.USER_INFO"
            :complete="currentPage > Pages.USER_INFO"
            :title="$t('user-registration.account-details')"
          />
          <v-divider />
          <v-stepper-item
            :value="Pages.PAGE_2"
            :complete="currentPage > Pages.PAGE_2"
            :title="$t('settings.site-settings')"
          />
          <v-divider />
          <v-stepper-item
            :value="Pages.CONFIRM"
            :complete="currentPage > Pages.CONFIRM"
            :title="$t('admin.maintenance.summary-title')"
          />
          <v-divider />
          <v-stepper-item
            :value="Pages.END"
            :complete="currentPage > Pages.END"
            :title="$t('admin.setup.setup-complete')"
          />
        </v-stepper-header>
        <v-progress-linear
          v-if="isSubmitting && currentPage === Pages.CONFIRM"
          color="primary"
          indeterminate
          class="mb-2"
        />

        <v-stepper-window :transition="false" class="stepper-window">
          <!-- LANDING -->
          <v-stepper-window-item :value="Pages.LANDING">
            <v-container class="mb-12">
              <AppLogo />
              <v-card-title class="text-h4 justify-center text-center text-break text-pre-wrap">
                {{ $t('admin.setup.welcome-to-mealie-get-started') }}
              </v-card-title>
              <v-btn
                :to="groupSlug ? `/g/${groupSlug}` : '/login'"
                rounded
                variant="outlined"
                color="grey-lighten-1"
                class="text-subtitle-2 d-flex mx-auto"
                style="width: fit-content;"
              >
                {{ $t('admin.setup.already-set-up-bring-to-homepage') }}
              </v-btn>
            </v-container>

            <v-card-actions class="justify-center flex-column py-8">
              <BaseButton
                size="large"
                color="primary"
                :icon="$globals.icons.translate"
                @click="langDialog = true"
              >
                {{ $t('language-dialog.choose-language') }}
              </BaseButton>
            </v-card-actions>

            <v-stepper-actions
              class="justify-end"
              :disabled="isSubmitting"
              next-text="general.next"
              @click:next="onNext"
            >
              <template #prev />
            </v-stepper-actions>
          </v-stepper-window-item>

          <!-- USER INFO -->
          <v-stepper-window-item :value="Pages.USER_INFO" eager>
            <v-container max-width="880">
              <UserRegistrationForm />
            </v-container>
            <v-stepper-actions
              :disabled="isSubmitting"
              prev-text="general.back"
              next-text="general.next"
              @click:prev="onPrev"
              @click:next="onNext"
            />
          </v-stepper-window-item>

          <!-- COMMON SETTINGS -->
          <v-stepper-window-item :value="Pages.PAGE_2">
            <v-container max-width="880">
              <v-card-title class="headline pa-0">
                {{ $t('admin.setup.common-settings-for-new-sites') }}
              </v-card-title>
              <AutoForm
                v-model="commonSettings"
                :items="commonSettingsForm"
              />
            </v-container>
            <v-stepper-actions
              :disabled="isSubmitting"
              prev-text="general.back"
              next-text="general.next"
              @click:prev="onPrev"
              @click:next="onNext"
            />
          </v-stepper-window-item>

          <!-- CONFIRMATION -->
          <v-stepper-window-item :value="Pages.CONFIRM">
            <v-container max-width="880">
              <v-card-title class="headline pa-0">
                {{ $t('general.confirm-how-does-everything-look') }}
              </v-card-title>
              <v-list>
                <template v-for="(item, idx) in confirmationData">
                  <v-list-item
                    v-if="item.display"
                    :key="idx"
                    class="px-0"
                  >
                    <v-list-item-title>{{ item.text }}</v-list-item-title>
                    <v-list-item-subtitle>{{ item.value }}</v-list-item-subtitle>
                  </v-list-item>
                  <v-divider
                    v-if="idx !== confirmationData.length - 1"
                    :key="`divider-${idx}`"
                  />
                </template>
              </v-list>
            </v-container>
            <v-stepper-actions
              :disabled="isSubmitting"
              prev-text="general.back"
              @click:prev="onPrev"
            >
              <template #next>
                <BaseButton
                  create
                  flat
                  :disabled="isSubmitting"
                  :loading="isSubmitting"
                  :icon="$globals.icons.check"
                  :text="$t('general.submit')"
                  @click="onNext"
                />
              </template>
            </v-stepper-actions>
          </v-stepper-window-item>

          <!-- END -->
          <v-stepper-window-item :value="Pages.END">
            <v-container max-width="880">
              <v-card-title class="text-h4 justify-center">
                {{ $t('admin.setup.setup-complete') }}
              </v-card-title>
              <v-card-title class="text-h6 justify-center">
                {{ $t('admin.setup.here-are-a-few-things-to-help-you-get-started') }}
              </v-card-title>
              <div
                v-for="link, idx in setupCompleteLinks"
                :key="idx"
                class="px-4 pt-4"
              >
                <div v-if="link.section">
                  <v-divider v-if="idx" />
                  <v-card-text class="headline pl-0">
                    {{ link.section }}
                  </v-card-text>
                </div>
                <v-btn
                  :to="link.to"
                  color="info"
                >
                  {{ link.text }}
                </v-btn>
                <v-card-text class="subtitle px-0 py-2">
                  {{ link.description }}
                </v-card-text>
              </div>
            </v-container>
            <v-stepper-actions
              :disabled="isSubmitting"
              prev-text="general.back"
              @click:prev="onPrev"
            >
              <template #next>
                <BaseButton
                  flat
                  color="primary"
                  :disabled="isSubmitting"
                  :loading="isSubmitting"
                  :icon="$globals.icons.home"
                  :text="$t('general.home')"
                  @click="onFinish"
                />
              </template>
            </v-stepper-actions>
          </v-stepper-window-item>
        </v-stepper-window>
      </v-stepper>

      <!-- Dialog Language -->
      <LanguageDialog v-model="langDialog" />
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { useDark } from "@vueuse/core";
import { useAdminApi, useUserApi } from "~/composables/api";
import { useLocales } from "~/composables/use-locales";
import { alert } from "~/composables/use-toast";
import { useUserRegistrationForm } from "~/composables/use-users/user-registration-form";
import { useCommonSettingsForm } from "~/composables/use-setup/common-settings-form";
import UserRegistrationForm from "~/components/Domain/User/UserRegistrationForm.vue";

definePageMeta({
  layout: "blank",
});

// ================================================================
// Setup
const i18n = useI18n();
const $auth = useMealieAuth();
const userApi = useUserApi();
const adminApi = useAdminApi();

const groupSlug = computed(() => $auth.user.value?.groupSlug);
const { locale } = useLocales();
const router = useRouter();
const isSubmitting = ref(false);
const langDialog = ref(false);
const isDark = useDark();

useSeoMeta({
  title: i18n.t("admin.setup.first-time-setup"),
});

if (!$auth.loggedIn.value) {
  router.push("/login");
}
else if (!$auth.user.value?.admin) {
  router.push(groupSlug.value ? `/g/${groupSlug.value}` : "/login");
}

enum Pages {
  LANDING = 0,
  USER_INFO = 1,
  PAGE_2 = 2,
  CONFIRM = 3,
  END = 4,
}

// ================================================================
// Forms
const { accountDetails, credentials } = useUserRegistrationForm();
const { commonSettingsForm } = useCommonSettingsForm();
const commonSettings = ref({
  makeGroupRecipesPublic: false,
  useSeedData: true,
});

const confirmationData = computed(() => {
  return [
    {
      display: true,
      text: i18n.t("user.email"),
      value: accountDetails.email.value,
    },
    {
      display: true,
      text: i18n.t("user.username"),
      value: accountDetails.username.value,
    },
    {
      display: true,
      text: i18n.t("user.full-name"),
      value: accountDetails.fullName.value,
    },
    {
      display: true,
      text: i18n.t("user.enable-advanced-content"),
      value: accountDetails.advancedOptions.value ? i18n.t("general.yes") : i18n.t("general.no"),
    },
    {
      display: true,
      text: i18n.t("group.enable-public-access"),
      value: commonSettings.value.makeGroupRecipesPublic ? i18n.t("general.yes") : i18n.t("general.no"),
    },
    {
      display: true,
      text: i18n.t("user-registration.use-seed-data"),
      value: commonSettings.value.useSeedData ? i18n.t("general.yes") : i18n.t("general.no"),
    },
  ];
});

const setupCompleteLinks = ref([
  {
    section: i18n.t("profile.data-migrations"),
    to: "/admin/backups",
    text: i18n.t("settings.backup.backup-restore"),
    description: i18n.t("admin.setup.restore-from-v1-backup"),
  },
  {
    to: "/group/migrations",
    text: i18n.t("migration.recipe-migration"),
    description: i18n.t("migration.coming-from-another-application-or-an-even-older-version-of-mealie"),
  },
  {
    section: i18n.t("recipe.create-recipes"),
    to: computed(() => `/g/${groupSlug.value || ""}/r/create/new`),
    text: i18n.t("recipe.create-recipe"),
    description: i18n.t("recipe.create-recipe-description"),
  },
  {
    to: computed(() => `/g/${groupSlug.value || ""}/r/create/url`),
    text: i18n.t("recipe.import-with-url"),
    description: i18n.t("recipe.scrape-recipe-description"),
  },
  {
    section: i18n.t("user.manage-users"),
    to: "/admin/manage/users",
    text: i18n.t("user.manage-users"),
    description: i18n.t("user.manage-users-description"),
  },
  {
    to: "/user/profile",
    text: i18n.t("profile.manage-user-profile"),
    description: i18n.t("admin.setup.manage-profile-or-get-invite-link"),
  },
]);

// ================================================================
// Page Navigation
const currentPage = ref(Pages.LANDING);

// ================================================================
// Page Submission

async function updateUser() {
  // Note: $auth.user is now a ref
  const { response } = await userApi.users.updateOne($auth.user.value!.id, {
    ...$auth.user.value,
    email: accountDetails.email.value,
    username: accountDetails.username.value,
    fullName: accountDetails.fullName.value,
    advanced: accountDetails.advancedOptions.value,
  });

  if (!response || response.status !== 200) {
    alert.error(i18n.t("events.something-went-wrong"));
  }
  else {
    $auth.refresh();
  }
}

async function updatePassword() {
  const { response } = await userApi.users.changePassword({
    currentPassword: "MyPassword",
    newPassword: credentials.password1.value,
  });

  if (!response || response.status !== 200) {
    alert.error(i18n.t("events.something-went-wrong"));
  }
}

async function submitRegistration() {
  // we update the password first, then update the user's details
  await updatePassword().then(updateUser);
}

async function updateGroup() {
  // Note: $auth.user is now a ref
  const { data } = await userApi.groups.getOne($auth.user.value!.groupId);
  if (!data || !data.preferences) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  const preferences = {
    ...data.preferences,
    privateGroup: !commonSettings.value.makeGroupRecipesPublic,
  };

  const payload = {
    ...data,
    preferences,
  };

  // Note: $auth.user is now a ref
  const { response } = await userApi.groups.updateOne($auth.user.value!.groupId, payload);
  if (!response || response.status !== 200) {
    alert.error(i18n.t("events.something-went-wrong"));
  }
}

async function updateHousehold() {
  // Note: $auth.user is now a ref
  const { data } = await adminApi.households.getOne($auth.user.value!.householdId);
  if (!data || !data.preferences) {
    alert.error(i18n.t("events.something-went-wrong"));
    return;
  }

  const preferences = {
    ...data.preferences,
    privateHousehold: !commonSettings.value.makeGroupRecipesPublic,
    recipePublic: commonSettings.value.makeGroupRecipesPublic,
  };

  const payload = {
    ...data,
    preferences,
  };

  // Note: $auth.user is now a ref
  const { response } = await adminApi.households.updateOne($auth.user.value!.householdId, payload);
  if (!response || response.status !== 200) {
    alert.error(i18n.t("events.something-went-wrong"));
  }
}

async function seedFoods() {
  const { response } = await userApi.seeders.foods({ locale: locale.value });
  if (!response || response.status !== 200) {
    alert.error(i18n.t("events.something-went-wrong"));
  }
}

async function seedUnits() {
  const { response } = await userApi.seeders.units({ locale: locale.value });
  if (!response || response.status !== 200) {
    alert.error(i18n.t("events.something-went-wrong"));
  }
}

async function seedLabels() {
  const { response } = await userApi.seeders.labels({ locale: locale.value });
  if (!response || response.status !== 200) {
    alert.error(i18n.t("events.something-went-wrong"));
  }
}

async function seedData() {
  if (!commonSettings.value.useSeedData) {
    return;
  }

  const tasks = [
    seedFoods(),
    seedUnits(),
    seedLabels(),
  ];

  await Promise.all(tasks);
}

async function submitCommonSettings() {
  const tasks = [
    updateGroup(),
    updateHousehold(),
    seedData(),
  ];

  await Promise.all(tasks);
}

async function submitAll() {
  const tasks = [
    submitRegistration(),
    submitCommonSettings(),
  ];

  await Promise.all(tasks);
}

async function handleSubmit(page: number) {
  if (isSubmitting.value) {
    return;
  }

  isSubmitting.value = true;
  switch (page) {
    case Pages.USER_INFO:
      if (await accountDetails.validate()) {
        currentPage.value += 1;
      }
      break;
    case Pages.CONFIRM:
      await submitAll();
      currentPage.value += 1;
      break;
    case Pages.END:
      router.push(groupSlug.value ? `/g/${groupSlug.value}` : "/login");
      break;
  }
  isSubmitting.value = false;
}

// ================================================================
// Stepper Navigation Handlers
function onPrev() {
  if (isSubmitting.value) return;
  if (currentPage.value > Pages.LANDING) currentPage.value -= 1;
}

async function onNext() {
  if (isSubmitting.value) return;
  if (currentPage.value === Pages.USER_INFO) {
    await handleSubmit(Pages.USER_INFO);
    return;
  }
  if (currentPage.value === Pages.CONFIRM) {
    await handleSubmit(Pages.CONFIRM);
    return;
  }
  currentPage.value += 1;
}

async function onFinish() {
  if (isSubmitting.value) return;
  await handleSubmit(Pages.END);
}
</script>

<style scoped>
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
</style>
