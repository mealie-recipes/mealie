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
import { getScaledRecipes } from "~/composables/use-group-mealplan";
import type { DaySection, Days, MealsByDate } from "~/composables/use-group-mealplan";

defineProps<{
  mealplans: MealsByDate[];
}>();
const i18n = useI18n();

function getDay(day: MealsByDate): Days {
  // Group only adjacent types so headings never change the saved meal order.
  const sections: DaySection[] = [];
  for (const meal of day.meals) {
    const last = sections.at(-1);
    if (last && last.meals[0].entryType === meal.entryType) {
      last.meals.push(meal);
    }
    else {
      sections.push({ title: i18n.t("meal-plan." + meal.entryType), meals: [meal] });
    }
  }
  return {
    date: day.date,
    sections,
    recipes: getScaledRecipes(day.meals),
  };
}
</script>
