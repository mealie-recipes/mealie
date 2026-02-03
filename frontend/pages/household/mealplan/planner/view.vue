<template>
  <v-container class="mx-0 my-3 pa">
    <v-row>
      <v-col
        v-for="(column, index) in allColumns"
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
                  {{ column.date === null ? $t('meal-plan.unassigned') : $d(column.date!, "short") }}
                </p>
              </v-col>
              <v-col class="d-flex align-center" cols="2">
                <GroupMealPlanDayContextMenu v-if="column.recipes.length" :recipes="column.recipes" />
              </v-col>
            </v-row>
          </v-container>
        </v-card>
        <div v-for="section in column.sections" :key="section.title">
          <div v-if="section.title" class="py-2 d-flex flex-column">
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
</template>

<script lang="ts" setup>
import type { MealsByDate } from "./types";
import type { ReadPlanEntry } from "~/lib/api/types/meal-plan";
import GroupMealPlanDayContextMenu from "~/components/Domain/Household/GroupMealPlanDayContextMenu.vue";
import RecipeCardMobile from "~/components/Domain/Recipe/RecipeCardMobile.vue";
import type { RecipeSummary } from "~/lib/api/types/recipe";

const props = defineProps<{
  mealplans: MealsByDate[];
  unassigned?: ReadPlanEntry[];
}>();

type DaySection = {
  title: string;
  meals: ReadPlanEntry[];
};

type Column = {
  date: Date | null;
  sections: DaySection[];
  recipes: RecipeSummary[];
};

const i18n = useI18n();

const plan = computed<Column[]>(() => {
  return props.mealplans.reduce((acc, day) => {
    const out: Column = {
      date: day.date,
      sections: [
        { title: i18n.t("meal-plan.breakfast"), meals: [] },
        { title: i18n.t("meal-plan.lunch"), meals: [] },
        { title: i18n.t("meal-plan.dinner"), meals: [] },
        { title: i18n.t("meal-plan.side"), meals: [] },
        { title: i18n.t("meal-plan.snack"), meals: [] },
        { title: i18n.t("meal-plan.drink"), meals: [] },
        { title: i18n.t("meal-plan.dessert"), meals: [] },
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
      else if (meal.entryType === "snack") {
        out.sections[4].meals.push(meal);
      }
      else if (meal.entryType === "drink") {
        out.sections[5].meals.push(meal);
      }
      else if (meal.entryType === "dessert") {
        out.sections[6].meals.push(meal);
      }

      if (meal.recipe) {
        out.recipes.push(meal.recipe);
      }
    }

    // Drop empty sections
    out.sections = out.sections.filter(section => section.meals.length > 0);

    acc.push(out);

    return acc;
  }, [] as Column[]);
});

const allColumns = computed<Column[]>(() => {
  const columns: Column[] = [];

  // Add unassigned column if it exists and has items
  if (props.unassigned && props.unassigned.length > 0) {
    columns.push({
      date: null,
      sections: [{ title: "", meals: props.unassigned }],
      recipes: props.unassigned.flatMap(meal => meal.recipe ? [meal.recipe] : []),
    });
  }

  // Add all day columns
  columns.push(...plan.value);

  return columns;
});
</script>
