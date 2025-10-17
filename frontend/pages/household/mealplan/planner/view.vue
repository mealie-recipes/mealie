<template>
  <div>
    <!-- Week Summary Header -->
    <v-card class="mb-4 pa-3">
      <div class="d-flex flex-wrap align-center justify-space-between">
        <div>
          <div class="text-h6">
            {{ $t("planner.totals.week-total") }}: {{ weekTotal.calories }} kcal
            <span class="text-body-2 text-medium-emphasis">
              ({{ $t("planner.totals.goal") }}: {{ weekGoalCalories }} kcal)
            </span>
          </div>
          <div class="text-body-2 text-medium-emphasis">
            {{ $t("planner.totals.daily-avg") }}: {{ dailyAvg.calories }} kcal
          </div>
          <div
            v-if="weekHasIncompleteData"
            class="text-caption text-warning mt-1"
            :title="$t('planner.tooltips.incomplete')"
          >
            {{ $t("planner.tooltips.incomplete") }}
          </div>
        </div>
        <div>
          <v-btn
            color="primary"
            variant="outlined"
            size="small"
            @click="goalsDialogOpen = true"
          >
            <v-icon start>
              {{ $globals.icons.cog }}
            </v-icon>
            {{ $t("planner.goals.button") }}
          </v-btn>
        </div>
      </div>
    </v-card>

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
            <v-container class="px-0 py-2">
              <!-- Datum -->
              <v-row no-gutters style="width: 100%;">
                <v-col cols="10" class="d-flex align-center">
                  <div class="pl-2">
                    <p class="my-0 font-weight-medium">
                      {{ $d(day.date, "short") }}
                    </p>
                  </div>
                </v-col>
                <v-col class="d-flex align-center justify-end" cols="2">
                  <!-- Platzhalter damit Höhe konsistent bleibt -->
                  <div style="width: 24px; height: 24px;">
                    <GroupMealPlanDayContextMenu v-if="day.recipes.length" :recipes="day.recipes" />
                  </div>
                </v-col>
              </v-row>
              <!-- Kalorien - direkt unter Datum, KEINE Labels -->
              <v-row no-gutters class="mt-1">
                <v-col cols="12" class="px-2">
                  <div class="text-body-2 font-weight-bold">
                    {{ getDayTotals(day.date).calories }} kcal
                  </div>
                  <!-- Makros - immer anzeigen für konsistente Höhe -->
                  <div class="text-caption text-medium-emphasis">
                    P {{ getDayTotals(day.date).protein }}g • C {{ getDayTotals(day.date).carbohydrate }}g • F {{ getDayTotals(day.date).fat }}g
                  </div>
                </v-col>
              </v-row>
            </v-container>
          </v-card>
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
      </v-col>
    </v-row>
  </v-container>

    <!-- Goals Dialog -->
    <PlannerGoalsDialog v-model="goalsDialogOpen" />
  </div>
</template>

<script lang="ts" setup>
import { format } from "date-fns";
import type { MealsByDate } from "./types";
import type { ReadPlanEntry } from "~/lib/api/types/meal-plan";
import type { RecipeSummary, Recipe } from "~/lib/api/types/recipe";
import GroupMealPlanDayContextMenu from "~/components/Domain/Household/GroupMealPlanDayContextMenu.vue";
import RecipeCardMobile from "~/components/Domain/Recipe/RecipeCardMobile.vue";
import PlannerGoalsDialog from "~/components/Domain/Planner/PlannerGoalsDialog.vue";
import { perOneServing, scaleForServings, sumMacros, type Macros } from "~/utils/nutrition";
import { usePlannerGoals } from "~/composables/use-planner-goals";
import { useUserApi } from "~/composables/api";

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
};

const i18n = useI18n();
const { goals } = usePlannerGoals();
const goalsDialogOpen = ref(false);

// API client for fetching full recipes
const api = useUserApi();

// Map to store full recipe data with nutrition
const recipesWithNutrition = ref<Map<string, Recipe>>(new Map());

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
        // Load full recipe with nutrition if not already loaded
        if (meal.recipe.id && !recipesWithNutrition.value.has(meal.recipe.id)) {
          loadRecipeNutrition(meal.recipe.id);
        }
      }
    }

    // Drop empty sections
    out.sections = out.sections.filter(section => section.meals.length > 0);

    acc.push(out);

    return acc;
  }, [] as Days[]);
});

/**
 * Load full recipe data including nutrition
 */
async function loadRecipeNutrition(recipeId: string) {
  try {
    const { data } = await api.recipes.getOne(recipeId);
    if (data) {
      recipesWithNutrition.value.set(recipeId, data);
    }
  } catch (error) {
    console.warn(`Failed to load nutrition for recipe ${recipeId}:`, error);
  }
}

/**
 * Calculate nutrition totals for each day
 * Returns a Map: dateString -> Macros
 */
const dayTotals = computed(() => {
  const totalsMap = new Map<string, Required<Macros>>();

  for (const mealDay of props.mealplans) {
    const dateKey = format(mealDay.date, "yyyy-MM-dd");
    const dayMacros: Required<Macros>[] = [];

    for (const meal of mealDay.meals) {
      if (!meal.recipe || !meal.recipe.id) {
        continue; // Skip entries without recipes
      }

      // Use full recipe from cache if available, otherwise skip
      const fullRecipe = recipesWithNutrition.value.get(meal.recipe.id);
      if (!fullRecipe) {
        continue; // Recipe not loaded yet
      }

      // Normalize to per-serving, then scale by planned servings
      const perServing = perOneServing(fullRecipe);
      const plannedServings = 1; // Default: assume 1 serving per meal plan entry
      // Note: ReadPlanEntry doesn't have a servings field, so we default to 1
      // If your API adds this field later, replace with: meal.servings || 1
      const scaled = scaleForServings(perServing, plannedServings);

      dayMacros.push(scaled);
    }

    // Sum all macros for this day
    const total = sumMacros(dayMacros);
    totalsMap.set(dateKey, total);
  }

  return totalsMap;
});

/**
 * Check if any recipe in the week is missing nutrition data
 */
const weekHasIncompleteData = computed(() => {
  for (const mealDay of props.mealplans) {
    for (const meal of mealDay.meals) {
      if (meal.recipe && meal.recipe.id) {
        const fullRecipe = recipesWithNutrition.value.get(meal.recipe.id);
        if (!fullRecipe || !fullRecipe.nutrition || !fullRecipe.nutrition.calories) {
          return true;
        }
      }
    }
  }
  return false;
});

/**
 * Week totals (sum of all days)
 */
const weekTotal = computed(() => {
  const allDayTotals = Array.from(dayTotals.value.values());
  return sumMacros(allDayTotals);
});

/**
 * Daily average
 */
const dailyAvg = computed(() => {
  const numDays = props.mealplans.length || 1;
  return {
    calories: Math.round(weekTotal.value.calories / numDays),
    protein: Math.round((weekTotal.value.protein / numDays) * 10) / 10,
    fat: Math.round((weekTotal.value.fat / numDays) * 10) / 10,
    carbohydrate: Math.round((weekTotal.value.carbohydrate / numDays) * 10) / 10,
    carbs: Math.round((weekTotal.value.carbs / numDays) * 10) / 10,
  };
});

/**
 * Week goal (calories * number of days)
 */
const weekGoalCalories = computed(() => {
  const numDays = props.mealplans.length || 1;
  return goals.value.calories * numDays;
});

/**
 * Get totals for a specific day
 */
function getDayTotals(date: Date): Required<Macros> {
  const dateKey = format(date, "yyyy-MM-dd");
  return (
    dayTotals.value.get(dateKey) || {
      calories: 0,
      protein: 0,
      fat: 0,
      carbohydrate: 0,
      carbs: 0,
    }
  );
}

/**
 * Get status for a day: 'under' | 'ok' | 'over'
 */
function getDayStatus(date: Date): "under" | "ok" | "over" {
  const totals = getDayTotals(date);
  const target = goals.value.calories;
  const tolerance = goals.value.toleranceKcal || 0;

  if (totals.calories < target - tolerance) {
    return "under";
  }
  if (totals.calories > target + tolerance) {
    return "over";
  }
  return "ok";
}

/**
 * Get color for day status chip
 */
function getDayStatusColor(date: Date): string {
  const status = getDayStatus(date);
  switch (status) {
    case "under":
      return "warning";
    case "over":
      return "error";
    case "ok":
    default:
      return "success";
  }
}
</script>
