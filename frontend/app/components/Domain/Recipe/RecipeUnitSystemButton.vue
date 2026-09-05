<template>
  <v-menu
    v-if="hasConvertibleIngredients"
    offset-y
    top
    nudge-top="6"
  >
    <template #activator="{ props: activatorProps }">
      <v-tooltip
        size="small"
        location="top"
        color="secondary-darken-1"
      >
        <template #activator="{ props: tooltipProps }">
          <v-card
            class="pa-1 px-2"
            dark
            color="secondary-darken-1"
            size="small"
            v-bind="{ ...activatorProps, ...tooltipProps }"
          >
            <v-icon size="small" class="mr-2">
              {{ $globals.icons.units }}
            </v-icon>
            <span>{{ activeLabel }}</span>
          </v-card>
        </template>
        <span>{{ $t("general.units") }}</span>
      </v-tooltip>
    </template>
    <v-list density="compact">
      <v-list-item
        v-for="option in options"
        :key="option.key"
        :active="option.value === unitSystem"
        @click="unitSystem = option.value"
      >
        <v-list-item-title>{{ option.text }}</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script setup lang="ts">
import { canConvertIngredient, useUnitSystem } from "~/composables/recipes";
import type { UnitSystem } from "~/composables/recipes/unit-systems";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe } from "~/lib/api/types/recipe";

const props = defineProps<{ recipe: NoUndefinedField<Recipe> }>();

const i18n = useI18n();
const { unitSystem } = useUnitSystem();

/**
 * Readers call US customary "imperial", so that's what the labels say. The stored value stays
 * `us`, which is what the units actually are, and leaves `imperial` free should a genuine
 * imperial ladder ever be added.
 */
const options = computed<{ key: string; value: UnitSystem | null; text: string }[]>(() => [
  { key: "as-written", value: null, text: i18n.t("recipe.unit-system.as-written") },
  { key: "metric", value: "metric", text: i18n.t("recipe.unit-system.metric-with-hint") },
  { key: "us", value: "us", text: i18n.t("recipe.unit-system.imperial-with-hint") },
]);

const activeLabel = computed(() => {
  switch (unitSystem.value) {
    case "metric":
      return i18n.t("recipe.unit-system.metric");
    case "us":
      return i18n.t("recipe.unit-system.imperial");
    default:
      return i18n.t("recipe.unit-system.as-written");
  }
});

// Hidden entirely when nothing on the recipe carries the standardization data conversion needs,
// so the control never appears only to do nothing when used.
const hasConvertibleIngredients = computed(() =>
  props.recipe.recipeIngredient.some(canConvertIngredient),
);
</script>
