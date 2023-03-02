<template>
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
      <v-card class="mb-2 border-left-primary rounded-sm pa-2">
        <p class="pl-2 mb-1">
          {{ $d(day.date, "short") }}
        </p>
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
          :route="mealplan.recipe ? true : false"
          :slug="mealplan.recipe ? mealplan.recipe.slug : mealplan.title"
          :description="mealplan.recipe ? mealplan.recipe.description : mealplan.text"
          :name="mealplan.recipe ? mealplan.recipe.name : mealplan.title"
        />
      </div>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";
import { MealsByDate } from "./types";
import { ReadPlanEntry } from "~/lib/api/types/meal-plan";
import RecipeCardMobile from "~/components/Domain/Recipe/RecipeCardMobile.vue";

export default defineComponent({
  components: {
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
    };

    const plan = computed<Days[]>(() => {
      return props.mealplans.reduce((acc, day) => {
        const out: Days = {
          date: day.date,
          sections: [
            { title: "Breakfast", meals: [] },
            { title: "Lunch", meals: [] },
            { title: "Dinner", meals: [] },
            { title: "Side", meals: [] },
          ],
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
