<template>
  <div class="plan-grid">
    <section
      v-for="(plan, index) in mealplans"
      :key="index"
      class="plan-grid__day mealie-card"
      :class="{ 'plan-grid__day--today': isToday(plan.date) }"
    >
      <slot v-bind="{ plan, index, day: getDay(plan) }" />
    </section>
  </div>
</template>

<script setup lang="ts">
import { isSameDay } from "date-fns";
import type { PlanEntryType } from "~/lib/api/types/meal-plan";

defineProps<{
  mealplans: MealsByDate[];
}>();
const planTypeOptions = usePlanTypeOptions();

function isToday(date: Date) {
  return isSameDay(date, new Date());
}

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

<style scoped>
.plan-grid {
  display: grid;
  /*
    RecipeCardMobile lays out a thumbnail + a favorite/rating/menu action row side by side,
    and needs about 320px before the "..." menu gets clipped, so columns never go narrower
  */
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
  align-items: start;
}

.plan-grid__day {
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: 18px 18px 14px;
}

.plan-grid__day--today {
  box-shadow: inset 0 0 0 2px rgba(var(--v-theme-primary), 0.55);
}

@media (max-width: 600px) {
  .plan-grid {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
