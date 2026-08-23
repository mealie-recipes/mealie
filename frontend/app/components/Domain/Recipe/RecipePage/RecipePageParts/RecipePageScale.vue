<template>
  <div class="d-flex justify-space-between align-center pt-2 pb-3">
    <RecipeScaleEditButton
      v-if="!isEditMode"
      v-model.number="scale"
      :recipe-servings="recipeServings"
      :edit-scale="hasFoodOrUnit && !isEditMode"
    />
    <RecipeUnitSystemToggle
      v-if="!isEditMode && hasConvertibleUnit"
      v-model:unit-system="unitSystem"
      v-model:temperature-unit="temperatureUnit"
    />
  </div>
</template>

<script setup lang="ts">
import RecipeScaleEditButton from "~/components/Domain/Recipe/RecipeScaleEditButton.vue";
import RecipeUnitSystemToggle from "~/components/Domain/Recipe/RecipeUnitSystemToggle.vue";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe } from "~/lib/api/types/recipe";
import type { TemperatureUnit, UnitSystem } from "~/lib/api/types/user";
import { usePageState } from "~/composables/recipe-page/shared-state";
import { hasTemperature } from "~/composables/recipes/use-unit-conversion";

const props = defineProps<{ recipe: NoUndefinedField<Recipe> }>();

const scale = defineModel<number>("scale", { default: 1 });
const unitSystem = defineModel<UnitSystem>("unitSystem", { default: "original" });
const temperatureUnit = defineModel<TemperatureUnit>("temperatureUnit", { default: "system" });

const { isEditMode } = usePageState(props.recipe.slug);

const recipeServings = computed<number>(() => {
  return props.recipe.recipeServings || props.recipe.recipeYieldQuantity || 1;
});

const hasFoodOrUnit = computed(() => {
  if (props.recipe.recipeIngredient) {
    for (const ingredient of props.recipe.recipeIngredient) {
      if (ingredient.food || ingredient.unit) {
        return true;
      }
    }
  }
  return false;
});

// Offering the toggle on a recipe where nothing can be converted is just a dead control.
// A unit only converts if an admin (or the seeder) gave it standardization data, but a
// recipe with no such units can still have an oven temperature worth converting.
const hasConvertibleUnit = computed(() =>
  (props.recipe.recipeIngredient ?? []).some(
    ingredient => ingredient.unit?.standardUnit && ingredient.unit.standardQuantity,
  )
  || (props.recipe.recipeInstructions ?? []).some(step => hasTemperature(step.text)),
);
</script>
