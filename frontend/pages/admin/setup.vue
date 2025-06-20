<template>
  <v-container fill-height
               fluid
               class="d-flex justify-center align-center"
               width="1200px"
               min-height="700px"
               :class="{
                 'bg-off-white': !$vuetify.theme.current.dark,
               }"
  >
    <BaseWizard v-model="currentPage"
                :max-page-number="totalPages"
                :title="$t('admin.setup.first-time-setup')"
                :prev-button-show="activeConfig.showPrevButton"
                :next-button-show="activeConfig.showNextButton"
                :next-button-text="activeConfig.nextButtonText"
                :next-button-icon="activeConfig.nextButtonIcon"
                :next-button-color="activeConfig.nextButtonColor"
                :next-button-is-submit="activeConfig.isSubmit"
                :is-submitting="isSubmitting"
                @submit="handleSubmit"
    >
      <v-container v-if="currentPage === Pages.LANDING"
                   class="mb-12"
      >
        <v-card-title class="text-h4 justify-center text-center">
          {{ $t('admin.setup.welcome-to-mealie-get-started') }}
        </v-card-title>
        <v-btn :to="groupSlug ? `/g/${groupSlug}` : '/login'"
               rounded
               variant="outlined"
               color="grey-lighten-1"
               class="text-subtitle-2 d-flex mx-auto"
               style="width: fit-content;"
        >
          {{ $t('admin.setup.already-set-up-bring-to-homepage') }}
        </v-btn>
      </v-container>
      <v-container v-if="currentPage === Pages.USER_INFO">
        <UserRegistrationForm />
      </v-container>
      <v-container v-if="currentPage === Pages.PAGE_2">
        <v-card-title class="headline justify-center">
          {{ $t('admin.setup.common-settings-for-new-sites') }}
        </v-card-title>
        <AutoForm v-model="commonSettings"
                  :items="commonSettingsForm"
        />
      </v-container>
      <v-container v-if="currentPage === Pages.CONFIRM">
        <v-card-title class="headline justify-center">
          {{ $t("general.confirm-how-does-everything-look") }}
        </v-card-title>
        <v-list>
          <template v-for="(item, idx) in confirmationData">
            <v-list-item v-if="item.display"
                         :key="idx"
            >
              <v-list-item-title> {{ item.text }} </v-list-item-title>
              <v-list-item-subtitle> {{ item.value }} </v-list-item-subtitle>
            </v-list-item>
            <v-divider v-if="idx !== confirmationData.length - 1"
                       :key="`divider-${idx}`"
            />
          </template>
        </v-list>
      </v-container>
      <v-container v-if="currentPage === Pages.END">
        <v-card-title class="text-h4 justify-center">
          {{ $t('admin.setup.setup-complete') }}
        </v-card-title>
        <v-card-title class="text-h6 justify-center">
          {{ $t('admin.setup.here-are-a-few-things-to-help-you-get-started') }}
        </v-card-title>
        <div v-for="link, idx in setupCompleteLinks"
             :key="idx"
             class="px-4 pt-4"
        >
          <div v-if="link.section">
            <v-divider v-if="idx" />
            <v-card-text class="headline pl-0">
              {{ link.section }}
            </v-card-text>
          </div>
          <v-btn :to="link.to"
                 color="info"
          >
            {{ link.text }}
          </v-btn>
          <v-card-text class="subtitle px-0 py-2">
            {{ link.description }}
          </v-card-text>
        </div>
      </v-container>
    </BaseWizard>
  </v-container>
</template>

<script lang="ts">
import { useAdminApi, useUserApi } from "~/composables/api";
import { useLocales } from "~/composables/use-locales";
import { alert } from "~/composables/use-toast";
import { useUserRegistrationForm } from "~/composables/use-users/user-registration-form";
import { useCommonSettingsForm } from "~/composables/use-setup/common-settings-form";
import UserRegistrationForm from "~/components/Domain/User/UserRegistrationForm.vue";

export default defineNuxtComponent({
  components: { UserRegistrationForm },
  setup() {
    definePageMeta({
      layout: "blank",
    });

    // ================================================================
    // Setup
    const i18n = useI18n();
    const $auth = useMealieAuth();
    const { $globals } = useNuxtApp();
    const userApi = useUserApi();
    const adminApi = useAdminApi();

    const groupSlug = computed(() => $auth.user.value?.groupSlug);
    const { locale } = useLocales();
    const router = useRouter();
    const isSubmitting = ref(false);
    useSeoMeta({
      title: i18n.t("admin.setup.first-time-setup"),
    });

    if (!$auth.loggedIn.value) {
      router.push("/login");
    }
    else if (!$auth.user.value?.admin) {
      router.push(groupSlug.value ? `/g/${groupSlug.value}` : "/login");
    }

		type Config = {
		  nextButtonText: string | undefined;
		  nextButtonIcon: string | undefined;
		  nextButtonColor: string | undefined;
		  showPrevButton: boolean;
		  showNextButton: boolean;
		  isSubmit: boolean;
		};

		const totalPages = 4;
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
		const currentPage = ref(0);
		const activeConfig = computed<Config>(() => {
		  const config: Config = {
		    nextButtonText: undefined,
		    nextButtonIcon: undefined,
		    nextButtonColor: undefined,
		    showPrevButton: true,
		    showNextButton: true,
		    isSubmit: false,
		  };

		  switch (currentPage.value) {
		    case Pages.LANDING:
		      config.showPrevButton = false;
		      config.nextButtonText = i18n.t("general.start");
		      config.nextButtonIcon = $globals.icons.forward;
		      break;
		    case Pages.USER_INFO:
		      config.showPrevButton = false;
		      config.nextButtonText = i18n.t("general.next");
		      config.nextButtonIcon = $globals.icons.forward;
		      config.isSubmit = true;
		      break;
		    case Pages.CONFIRM:
		      config.isSubmit = true;
		      break;
		    case Pages.END:
		      config.nextButtonText = i18n.t("general.home");
		      config.nextButtonIcon = $globals.icons.home;
		      config.nextButtonColor = "primary";
		      config.showPrevButton = false;
		      config.isSubmit = true;
		      break;
		  }

		  return config;
		});

		// ================================================================
		// Page Submission

		async function updateUser() {
		  // Note: $auth.user is now a ref
		  const { response } = await userApi.users.updateOne($auth.user.value!.id, {
		    ...$auth.user.value,
		    email: accountDetails.email.value,
		    username: accountDetails.username.value,
		    fullName: accountDetails.fullName.value,
		    advancedOptions: accountDetails.advancedOptions.value,
		  });

		  if (!response || response.status !== 200) {
		    alert.error(i18n.t("events.something-went-wrong"));
		  }
		  else {
		    $auth.refresh();
		    /* $auth.setUser({
					...$auth.user.value,
					email: accountDetails.email.value,
					username: accountDetails.username.value,
					fullName: accountDetails.fullName.value,
				}) */
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
		  // the backend will only update the password without the "currentPassword" field if the user is the default user,
		  // so we update the password first, then update the user's details
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

		return {
		  // Setup
		  groupSlug,
		  // Forms
		  commonSettingsForm,
		  commonSettings,
		  confirmationData,
		  setupCompleteLinks,
		  // Page Navigation
		  Pages,
		  currentPage,
		  totalPages,
		  activeConfig,
		  // Page Submission
		  isSubmitting,
		  handleSubmit,
		};
  },
});
</script>
