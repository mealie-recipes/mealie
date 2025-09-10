<template>
  <div v-if="preferences">
    <BaseCardSectionTitle :title="$t('group.general-preferences')" />
    <v-checkbox
      v-model="preferences.privateGroup"
      class="mt-n4"
      :label="$t('group.private-group')"
    />
  </div>
</template>

<script setup lang="ts">
import type { ReadGroupPreferences } from "~/lib/api/types/user";

const preferences = defineModel<ReadGroupPreferences>({ required: true });
</script>

<style lang="scss" scoped></style>
