<template>
  <v-menu
    location="bottom end"
    :offset="6"
    close-delay="50"
  >
    <template #activator="{ props: menuProps }">
      <slot name="activator" :props="menuProps" />
    </template>
    <v-list
      density="comfortable"
      class="mb-0 mt-1 py-0"
      variant="flat"
      min-width="260"
    >
      <template v-for="item in createLinks" :key="item.title">
        <template v-if="!item.hide">
          <v-divider
            v-if="item.insertDivider"
            class="mx-2"
          />
          <v-list-item
            :to="item.to"
            exact
            class="my-1"
          >
            <template #prepend>
              <v-icon
                size="28"
                :icon="item.icon"
                color="primary"
              />
            </template>
            <v-list-item-title class="font-weight-medium" style="font-size: small;">
              {{ item.title }}
            </v-list-item-title>
            <v-list-item-subtitle class="font-weight-medium" style="font-size: small;">
              {{ item.subtitle }}
            </v-list-item-subtitle>
          </v-list-item>
        </template>
      </template>
    </v-list>
  </v-menu>
</template>

<script setup lang="ts">
import { useGroupSelf } from "~/composables/use-groups";

const i18n = useI18n();
const { $globals } = useNuxtApp();
const auth = useMealieAuth();
const route = useRoute();
const { group } = useGroupSelf();

const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");
const showAIImport = computed(() => group.value?.aiProviderSettings?.aiEnabled);

const createLinks = computed(() => [
  {
    insertDivider: false,
    icon: $globals.icons.link,
    title: i18n.t("general.import"),
    subtitle: i18n.t("new-recipe.import-by-url"),
    to: `/g/${groupSlug.value}/r/create/url`,
    hide: false,
  },
  {
    insertDivider: false,
    icon: $globals.icons.autoFix,
    title: i18n.t("recipe.import-with-ai"),
    subtitle: i18n.t("recipe.import-with-ai-subtitle"),
    to: `/g/${groupSlug.value}/r/create/ai`,
    hide: !showAIImport.value,
  },
  {
    insertDivider: true,
    icon: $globals.icons.edit,
    title: i18n.t("general.create"),
    subtitle: i18n.t("new-recipe.create-manually"),
    to: `/g/${groupSlug.value}/r/create/new`,
    hide: false,
  },
]);
</script>
