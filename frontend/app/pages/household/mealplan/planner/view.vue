<template>
  <v-container class="mx-0 my-3">
    <v-row>
      <v-col
        v-for="(day, index) in plan"
        :key="index"
        cols="12"
        sm="12"
        md="6"
        lg="4"
        xl="3"
        xxl="2"
        class="col-borders my-1 d-flex flex-column"
      >
        <v-card class="mb-2 border-left-primary rounded-sm px-2">
          <v-container class="px-0 d-flex align-center" style="height: 56px">
            <v-row no-gutters style="width: 100%;">
              <v-col cols="10" class="d-flex align-center">
                <p class="pl-2 my-1" :class="{ 'text-primary': isToday(day.date) }">
                  {{ $d(day.date, "short") }}
                </p>
              </v-col>
              <v-col class="d-flex align-center" cols="2">
                <GroupMealPlanDayContextMenu v-if="day.recipes.length" :recipes="day.recipes" />
              </v-col>
            </v-row>
          </v-container>
        </v-card>
        <div v-for="section in day.sections" :key="section.type">
          <div class="pt-3 pb-1 d-flex flex-column">
            <p class="text-overline my-0">
              {{ section.title }}
            </p>
          </div>

          <RecipeCardMobile
            v-for="mealplan in section.meals"
            :key="mealplan.id"
            :recipe-id="mealplan.recipe ? mealplan.recipe.id! : ''"
            class="mb-2"
            :rating="mealplan.recipe ? mealplan.recipe.rating! : 0"
            :slug="mealplan.recipe ? mealplan.recipe.slug! : ''"
            :description="mealplan.recipe ? mealplan.recipe.description! : mealplan.text!"
            :name="mealplan.recipe ? mealplan.recipe.name! : mealplan.title!"
            :image="mealplan.recipe ? mealplan.recipe.image! : undefined"
            :tags="mealplan.recipe ? mealplan.recipe.tags! : []"
          />
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { isSameDay } from "date-fns";

import type { PlanEntryType, ReadPlanEntry } from "~/lib/api/types/meal-plan";
import { usePlanTypeOptions } from "~/composables/use-group-mealplan";
import GroupMealPlanDayContextMenu from "~/components/Domain/Household/GroupMealPlanDayContextMenu.vue";
import RecipeCardMobile from "~/components/Domain/Recipe/RecipeCardMobile.vue";
import type { RecipeSummary } from "~/lib/api/types/recipe";

export type MealsByDate = {
  date: Date;
  meals: ReadPlanEntry[];
};

const props = defineProps<{
  mealplans: MealsByDate[];
}>();

type DaySection = {
  type: PlanEntryType;
  title: string;
  meals: ReadPlanEntry[];
};

type Days = {
  date: Date;
  sections: DaySection[];
  recipes: RecipeSummary[];
};

const i18n = useI18n();
const planTypeOptions = usePlanTypeOptions();

const plan = computed<Days[]>(() => {
  return props.mealplans.map((day) => {
    return {
      date: day.date,
      sections: planTypeOptions
        .map(({ value }) => ({
          type: value,
          title: i18n.t(`meal-plan.${value}`),
          meals: day.meals.filter(meal => meal.entryType === value),
        }))
        // Drop empty sections
        .filter(section => section.meals.length),
      recipes: day.meals.flatMap(meal => meal.recipe ?? []),
    };
  });
});

const isToday = (date: Date) => {
  return isSameDay(date, new Date());
};
</script>

<style scoped>
/*
  RecipeCardMobile lays out a fixed-width thumbnail + a favorite/rating/menu action row
  side-by-side. Below ~320px the action row no longer fits and the "..." menu button gets
  clipped by the card's overflow:hidden. Enforcing a min-width here makes the day columns
  wrap to fewer per row instead of shrinking past that point.
*/
.col-borders {
  min-width: 340px;
}
</style>
