<template>
  <div class="d-flex justify-space-between align-center pt-2 pb-3">
    <RecipeScaleEditButton
      v-if="!isEditMode"
      v-model.number="scale"
      :recipe-servings="recipeServings"
      :edit-scale="hasFoodOrUnit && !isEditMode"
    />
    <RecipeUnitSystemToggle
      v-if="!isEditMode && hasFoodOrUnit"
      v-model="unitSystem"
    />
  </div>
</template>

<script setup lang="ts">
import RecipeScaleEditButton from "~/components/Domain/Recipe/RecipeScaleEditButton.vue";
import RecipeUnitSystemToggle from "~/components/Domain/Recipe/RecipeUnitSystemToggle.vue";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe } from "~/lib/api/types/recipe";
import type { UnitSystem } from "~/lib/api/types/user";
import { usePageState } from "~/composables/recipe-page/shared-state";

const props = defineProps<{ recipe: NoUndefinedField<Recipe> }>();

const scale = defineModel<number>("scale", { default: 1 });
const unitSystem = defineModel<UnitSystem>("unitSystem", { default: "original" });

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
</script>
