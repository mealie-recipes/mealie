<template>
  <div v-if="preferences">
    <BaseCardSectionTitle :title="$t('group.group-preferences')" />
    <div class="mb-6">
      <v-checkbox
        v-model="local.privateGroup"
        hide-details
        density="compact"
        color="primary"
        :label="$t('group.private-group')"
      />
      <div class="ml-8">
        <p class="text-subtitle-2 my-0 py-0">
          {{ $t("group.private-group-description") }}
        </p>
        <DocLink
          class="mt-2"
          link="/documentation/getting-started/faq/#how-do-private-groups-and-recipes-work"
        />
      </div>
    </div>
    <div class="mb-6">
      <v-checkbox
        v-model="local.showAnnouncements"
        hide-details
        density="compact"
        color="primary"
        :label="$t('announcements.show-announcements-from-mealie')"
      />
      <div class="ml-8">
        <p class="text-subtitle-2 my-0 py-0">
          {{ $t("announcements.show-announcements-setting-description") }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ReadGroupPreferences } from "~/lib/api/types/user";

const preferences = defineModel<ReadGroupPreferences>({ required: true });
const local = reactive({ ...preferences.value });
watch(local, (newVal) => { preferences.value = { ...newVal }; });
</script>
