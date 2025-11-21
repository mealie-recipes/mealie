<template>
  <v-container class="mx-0 my-3 pa">
    <v-row>
      <v-col
        v-for="(day, index) in plan"
        :key="index"
        cols="12"
        sm="12"
        md="4"
        lg="4"
        xl="2"
        class="col-borders my-1 d-flex flex-column"
      >
        <v-card class="mb-2 border-left-primary rounded-sm px-2">
          <v-container class="px-0 d-flex align-center" height="56px">
            <v-row no-gutters style="width: 100%;">
              <v-col cols="10" class="d-flex align-center">
                <p class="pl-2 my-1">
                  {{ $d(day.date, "short") }}
                </p>
              </v-col>
              <v-col class="d-flex align-center" cols="2">
                <GroupMealPlanDayContextMenu
                  v-if="day.recipes.length"
                  :recipes="day.recipes"
                  :date="day.date"
                  @show-nutrition="onShowNutrition"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-card>
        <div v-if="(showNutritionByDate[dateKey(day.date)]?.show) && (showNutritionByDate[dateKey(day.date)]?.nutrition)" class="mb-2">
          <v-card class="pa-2 mb-2 border-left-accent rounded-sm">
            <RecipeNutrition
              v-model="showNutritionByDate[dateKey(day.date)]!.nutrition"
              class="mt-4"
              :edit="false"
              :mealplan="true"
              @close-nutrition="() => onCloseNutrition(day.date)"
            />
          </v-card>
        </div>
        <div v-else>
          <div v-for="section in day.sections" :key="section.title">
            <div class="py-2 d-flex flex-column">
              <div class="primary" style="width: 50px; height: 2.5px" />
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
              :slug="mealplan.recipe ? mealplan.recipe.slug! : mealplan.title!"
              :description="mealplan.recipe ? mealplan.recipe.description! : mealplan.text!"
              :name="mealplan.recipe ? mealplan.recipe.name! : mealplan.title!"
              :tags="mealplan.recipe ? mealplan.recipe.tags! : []"
            />
          </div>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import type { MealsByDate, NutritionByDate } from "./types";
import type { ReadPlanEntry } from "~/lib/api/types/meal-plan";
import GroupMealPlanDayContextMenu from "~/components/Domain/Household/GroupMealPlanDayContextMenu.vue";
import RecipeCardMobile from "~/components/Domain/Recipe/RecipeCardMobile.vue";
import type { Nutrition, RecipeSummary } from "~/lib/api/types/recipe";
import { alert } from "~/composables/use-toast";
import RecipeNutrition from "~/components/Domain/Recipe/RecipeNutrition.vue";

const props = defineProps<{
  mealplans: MealsByDate[];
}>();

type DaySection = {
  title: string;
  meals: ReadPlanEntry[];
};

type Days = {
  date: Date;
  sections: DaySection[];
  recipes: RecipeSummary[];
  nutrition?: Record<string, number>;
};

const i18n = useI18n();

const plan = computed<Days[]>(() => {
  return props.mealplans.reduce((acc, day) => {
    const out: Days = {
      date: day.date,
      sections: [
        { title: i18n.t("meal-plan.breakfast"), meals: [] },
        { title: i18n.t("meal-plan.lunch"), meals: [] },
        { title: i18n.t("meal-plan.dinner"), meals: [] },
        { title: i18n.t("meal-plan.side"), meals: [] },
      ],
      recipes: [],
      nutrition: {},
    };

    for (const meal of day.meals) {
      if (meal.entryType === "breakfast") {
        out.sections[0].meals.push(meal);
      }
      else if (meal.entryType === "lunch") {
        out.sections[1].meals.push(meal);
      }
      else if (meal.entryType === "dinner") {
        out.sections[2].meals.push(meal);
      }
      else if (meal.entryType === "side") {
        out.sections[3].meals.push(meal);
      }

      if (meal.recipe) {
        out.recipes.push(meal.recipe);
      }
    }

    // Drop empty sections
    out.sections = out.sections.filter(section => section.meals.length > 0);

    acc.push(out);

    return acc;
  }, [] as Days[]);
});

// map of YYYY-MM-DD -> NutritionByDate for each day
const showNutritionByDate = ref<Record<string, NutritionByDate>>({});

function dateKey(d: Date | string | null | undefined) {
  if (!d) return "";
  const dt = d instanceof Date ? d : new Date(d);
  return dt.toISOString().slice(0, 10); // YYYY-MM-DD
}

async function sumNutritionForDay(recipes?: RecipeSummary[]): Promise<Nutrition> {
  const nutritionTotals: { [key: string]: number } = {};
  for (const recipe of recipes || []) {
    const nutrition = recipe.nutrition;
    if (nutrition) {
      for (const [key, value] of Object.entries(nutrition)) {
        const numValue = parseFloat(value as unknown as string);

        if (numValue && !isNaN(numValue)) {
          if (!nutritionTotals[key]) {
            nutritionTotals[key] = 0;
          }
          nutritionTotals[key] += numValue;
          nutritionTotals[key] = Math.round(nutritionTotals[key] * 100) / 100;
        }
      }
    }
  }
  const nutritionTyped: Nutrition = {};
  for (const [key, value] of Object.entries(nutritionTotals)) {
    nutritionTyped[key] = value;
  }

  return nutritionTyped;
}

function onShowNutrition(payload: Date) {
  const date = payload;
  sumNutritionForDay(plan.value.find(day => dateKey(day.date) === dateKey(date))?.recipes).then((nutritionForDay) => {
    if (!nutritionForDay || Object.keys(nutritionForDay).length === 0) {
      // no nutrition to show
      alert.error(i18n.t("recipe.no-nutrition-values") as string);
      return;
    }
    const key = dateKey(date);
    if (!key) return;

    showNutritionByDate.value = {
      ...showNutritionByDate.value,
      [key]: {
        show: !(showNutritionByDate.value[key]?.show ?? false),
        date: date,
        nutrition: nutritionForDay,
      },
    };
  });
}

function onCloseNutrition(date: Date) {
  const key = dateKey(date);
  if (!key) return;
  const current = showNutritionByDate.value[key];
  if (!current) return;
  showNutritionByDate.value = {
    ...showNutritionByDate.value,
    [key]: { ...current, show: false },
  };
}
</script>
