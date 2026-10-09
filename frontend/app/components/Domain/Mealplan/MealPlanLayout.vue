<template>
  <v-row>
    <v-col
      v-for="(plan, index) in mealplans"
      :key="index"
      cols="12"
      sm="12"
      md="12"
      lg="6"
      xl="4"
      xxl="4"
      class="col-borders my-1 d-flex flex-column"
    >
      <slot v-bind="{ plan, index, day: getDay(plan) }" />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import type { PlanEntryType } from "~/lib/api/types/meal-plan";

defineProps<{
  mealplans: MealsByDate[];
}>();
const planTypeOptions = usePlanTypeOptions();

function getDay(day: MealsByDate): Days {
  const forSection = (key: PlanEntryType) => day.meals.filter(({ entryType }) => entryType === key);
  return {
    date: day.date,
    sections: planTypeOptions
      .map(({ text, value }) => ({ title: text, meals: forSection(value) }))
      .filter(({ meals }) => meals.length > 0),
    recipes: day.meals.flatMap(({ recipe }) => recipe ? [recipe] : []),
  };
}
</script>
