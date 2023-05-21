<template>
  <div id="mealplan-container" ref="mealplan-container">
    <button class="scroll-arrow scroll-prev" @click="scrollToNext(false)">&lt;&lt;&lt;</button>
    <v-col
      v-for="(day, index) in plan"
      ref="days"
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
          :recipe-id="(mealplan.recipe && mealplan.recipe.id) ? mealplan.recipe.id : ''"
          class="mb-2"
          :route="mealplan.recipe ? true : false"
          :rating="mealplan.recipe ? mealplan.recipe.rating : 0"
          :slug="(mealplan.recipe ? mealplan.recipe.slug : mealplan.title) || 'Recipe'"
          :description="(mealplan.recipe ? mealplan.recipe.description : mealplan.text) || 'No Description'"
          :name="(mealplan.recipe ? mealplan.recipe.name : mealplan.title) || 'Recipe'"
        />
      </div>
    </v-col>
    <button class="scroll-arrow scroll-next" @click="scrollToNext(true)">&gt;&gt;&gt;</button>
  </div>
</template>


<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
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
  methods: {
    scrollToNext(forward: boolean) {
      if(this.$refs.days && this.$refs["mealplan-container"]) {
        const daysRefs = this.$refs.days as HTMLDivElement[];
        const containerRef = this.$refs["mealplan-container"] as HTMLDivElement
        const containerOffset = containerRef.offsetLeft;
        let scrollLeft: number[] = daysRefs.map((day) => day.offsetLeft - containerRef.scrollLeft - containerOffset);
        if(forward) {
          scrollLeft = scrollLeft.filter(n => n > 0);
        scrollLeft.sort((a,b) => a-b);
        } else {
          scrollLeft = scrollLeft.filter(n => n < 0);
        scrollLeft.sort((a,b) => b-a);
        }
        containerRef.scrollTo({
          left: scrollLeft[0] + containerRef.scrollLeft ,
          behavior: "smooth"
        });;
      } else {
        console.log("Unable to perform scrolling due to missing ref")
      }
    }
  },
});
</script>

<style>
#mealplan-container {
  display: flex;
  flex-direction: row;
  margin: -12px 12px -12px 12px;
  overflow: auto;
}

.scroll-arrow {
  position: absolute;
  top: 200px;
}

.scroll-next {
  right: 5px
}

.scroll-prev {
  left: 0px
}

</style>
