<template>
  <RecipeScaleEditButton
    v-model="scale"
    :recipe-servings="recipeServings"
    edit-scale
  />
</template>

<script setup lang="ts">
import RecipeScaleEditButton from "~/components/Domain/Recipe/RecipeScaleEditButton.vue";
import type { useMealplans } from "~/composables/use-group-mealplan";
import { useMealPlanScale } from "~/composables/use-mealplan-scale";
import type { ReadPlanEntry } from "~/lib/api/types/meal-plan";

const props = defineProps<{
  meal: ReadPlanEntry;
  actions: ReturnType<typeof useMealplans>["actions"];
}>();

const { scale, recipeServings } = useMealPlanScale(
  () => props.meal,
  payload => props.actions.updateOne(payload),
);
</script>
