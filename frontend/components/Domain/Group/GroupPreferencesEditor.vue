<template>
  <div v-if="preferences">
    <BaseCardSectionTitle :title="$t('group.general-preferences')" />
    <v-checkbox
      v-model="preferences.privateGroup"
      class="mt-n4"
      :label="$t('group.private-group')"
    />
    <v-select
      v-model="preferences.pluralHandling"
      :hint="$t('group.plural-handling-description')"
      persistent-hint
      :items="pluralHandlingOptions"
      :item-props="pluralHandlingOptionsItemProps"
      :label="$t('group.plural-handling')"
      item-title="label"
      item-value="value"
    />
  </div>
</template>

<script setup lang="ts">
import type { ReadGroupPreferences } from "~/lib/api/types/group";
import { useGroupPluralHandlingOptions } from "~/composables/use-group-plural-handling-options";

const preferences = defineModel<ReadGroupPreferences>({ required: true });

const i18n = useI18n();
const { pluralHandlingOptions, pluralHandlingOptionsItemProps } = useGroupPluralHandlingOptions(i18n);
</script>

<style lang="scss" scoped></style>
