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
          <v-container class="px-0">
            <v-row no-gutters style="width: 100%;">
              <v-col cols="10">
                <p class="pl-2 my-1">
                  {{ $d(day.date, "short") }}
                </p>
              </v-col>
              <v-col class="d-flex justify-top" cols="2">
                <GroupMealPlanDayContextMenu v-if="day.recipes.length" :recipes="day.recipes" />
              </v-col>
            </v-row>
          </v-container>
        </v-card>
        <div v-for="section in day.sections" :key="section.title">
          <div class="py-2 d-flex flex-column">
            <div class="primary" style="width: 50px; height: 2.5px"></div>
            <p class="text-overline my-0">
              {{ section.title }}
            </p>
          </div>

          <RecipeCardMobile
            v-for="mealplan in section.meals"
            :key="mealplan.id"
            :recipe-id="mealplan.recipe ? mealplan.recipe.id : ''"
            class="mb-2"
            :rating="mealplan.recipe ? mealplan.recipe.rating : 0"
            :slug="mealplan.recipe ? mealplan.recipe.slug : mealplan.title"
            :description="mealplan.recipe ? mealplan.recipe.description : mealplan.text"
            :name="mealplan.recipe ? mealplan.recipe.name : mealplan.title"
            :tags="mealplan.recipe ? mealplan.recipe.tags : []"
          />
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
import { MealsByDate } from "./types";
import { ReadPlanEntry } from "~/lib/api/types/meal-plan";
import GroupMealPlanDayContextMenu from "~/components/Domain/Household/GroupMealPlanDayContextMenu.vue";
import RecipeCardMobile from "~/components/Domain/Recipe/RecipeCardMobile.vue";
import { RecipeSummary } from "~/lib/api/types/recipe";

export default defineComponent({
  components: {
    GroupMealPlanDayContextMenu,
    RecipeCardMobile,
  },
  props: {
    mealplans: {
      type: Array as () => MealsByDate[],
      required: true,
    },
  },
  setup(props) {
    type DaySection = {
      title: string;
      meals: ReadPlanEntry[];
    };

    type Days = {
      date: Date;
      sections: DaySection[];
      recipes: RecipeSummary[];
    };

  const { i18n } = useContext();

    const plan = computed<Days[]>(() => {
      return props.mealplans.reduce((acc, day) => {
        const out: Days = {
          date: day.date,
          sections: [
            { title: i18n.tc("meal-plan.breakfast"), meals: [] },
            { title: i18n.tc("meal-plan.lunch"), meals: [] },
            { title: i18n.tc("meal-plan.dinner"), meals: [] },
            { title: i18n.tc("meal-plan.side"), meals: [] },
          ],
          recipes: [],
        };

        for (const meal of day.meals) {
          if (meal.entryType === "breakfast") {
            out.sections[0].meals.push(meal);
          } else if (meal.entryType === "lunch") {
            out.sections[1].meals.push(meal);
          } else if (meal.entryType === "dinner") {
            out.sections[2].meals.push(meal);
          } else if (meal.entryType === "side") {
            out.sections[3].meals.push(meal);
          }

          if (meal.recipe) {
            out.recipes.push(meal.recipe);
          }
        }

        // Drop empty sections
        out.sections = out.sections.filter((section) => section.meals.length > 0);

        acc.push(out);

        return acc;
      }, [] as Days[]);
    });

    return {
      plan,
    };
  },
});
</script>
