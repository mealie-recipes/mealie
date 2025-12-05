<template>
  <v-container max-width="880" class="end-page-content">
    <div class="d-flex flex-column ga-6">
      <div>
        <v-card-title class="text-h4 justify-center">
          {{ $t('admin.setup.setup-complete') }}
        </v-card-title>
        <v-card-subtitle class="justify-center">
          {{ $t('admin.setup.here-are-a-few-things-to-help-you-get-started') }}
        </v-card-subtitle>
      </div>
      <div
        v-for="section, idx in sections"
        :key="idx"
        class="d-flex flex-column ga-3"
      >
        <v-card-title class="text-h6 pl-0">
          {{ section.title }}
        </v-card-title>
        <div class="sections d-flex flex-column ga-2">
          <v-card
            v-for="link, linkIdx in section.links"
            :key="linkIdx"
            clas="link-card"
            :href="link.to"
            :title="link.text"
            :subtitle="link.description"
            :append-icon="$globals.icons.chevronRight"
          >
            <template #prepend>
              <v-avatar :icon="link.icon || undefined" variant="tonal" :color="section.color" />
            </template>
          </v-card>
        </div>
      </div>
    </div>
  </v-container>
</template>

<script lang="ts">
export default defineNuxtComponent({
  setup() {
    const i18n = useI18n();
    const $auth = useMealieAuth();
    const groupSlug = computed(() => $auth.user.value?.groupSlug);
    const { $globals } = useNuxtApp();

    const sections = ref([
      {
        title: i18n.t("profile.data-migrations"),
        color: "info",
        links: [
          {
            icon: $globals.icons.backupRestore,
            to: "/admin/backups",
            text: i18n.t("settings.backup.backup-restore"),
            description: i18n.t("admin.setup.restore-from-v1-backup"),
          },
          {
            icon: $globals.icons.import,
            to: "/group/migrations",
            text: i18n.t("migration.recipe-migration"),
            description: i18n.t("migration.coming-from-another-application-or-an-even-older-version-of-mealie"),
          },
        ],
      },
      {
        title: i18n.t("recipe.create-recipes"),
        color: "success",
        links: [
          {
            icon: $globals.icons.createAlt,
            to: computed(() => `/g/${groupSlug.value || ""}/r/create/new`),
            text: i18n.t("recipe.create-recipe"),
            description: i18n.t("recipe.create-recipe-description"),
          },
          {
            icon: $globals.icons.link,
            to: computed(() => `/g/${groupSlug.value || ""}/r/create/url`),
            text: i18n.t("recipe.import-with-url"),
            description: i18n.t("recipe.scrape-recipe-description"),
          },
        ],
      },
      {
        title: i18n.t("user.manage-users"),
        color: "primary",
        links: [
          {
            icon: $globals.icons.group,
            to: "/admin/manage/users",
            text: i18n.t("user.manage-users"),
            description: i18n.t("user.manage-users-description"),
          },
          {
            icon: $globals.icons.user,
            to: "/user/profile",
            text: i18n.t("profile.manage-user-profile"),
            description: i18n.t("admin.setup.manage-profile-or-get-invite-link"),
          },
        ],
      },
    ]);
    return { sections };
  },
});
</script>

<style>
.v-container {
  .v-card-title,
  .v-card-subtitle {
    padding: 0;
    white-space: unset;
  }

  .v-card-item {
    gap: 0.5rem;
  }
}
</style>
