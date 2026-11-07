<template>
  <v-row>
    <!-- weeks span the full row, so each week's days start on a new row below it -->
    <v-col
      v-for="(plan, index) in mealplans"
      :key="index"
      v-bind="plan.endDate ? WEEK_COLS : DAY_COLS"
      class="col-borders my-1 d-flex flex-column"
      :class="{ 'week-section': plan.endDate, 'mt-6': plan.endDate && index > 0, 'out-of-range': plan.outOfRange }"
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

const DAY_COLS = { cols: 12, sm: 12, md: 12, lg: 6, xl: 4, xxl: 4 };
const WEEK_COLS = { cols: 12 };

function getDay(day: MealsByDate): Days {
  const forSection = (key: PlanEntryType) => day.meals.filter(({ entryType }) => entryType === key);
  return {
    date: day.date,
    endDate: day.endDate,
    outOfRange: day.outOfRange,
    sections: planTypeOptions
      .map(({ text, value }) => ({ title: text, meals: forSection(value) }))
      .filter(({ meals }) => meals.length > 0),
    recipes: getScaledRecipes(day.meals),
  };
}
</script>

<style scoped>
/* a light tint of the week header's color, so the whole week reads as one block apart from the days */
.week-section {
  background-color: rgba(var(--v-theme-primary), 0.08);
  border-radius: 4px;
}

/* days outside the selected range only complete their week: still there to plan in, but set back */
.out-of-range {
  opacity: 0.45;
}

/* a week spans the full row, so its meals are laid out side by side instead of in one long column */
:deep(.week-meals) {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  column-gap: 8px;
}
</style>
