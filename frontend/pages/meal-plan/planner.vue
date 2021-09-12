<template>
  <v-container>
    <v-card>
      <v-card-title class="headline">New Recipe</v-card-title>
      <v-card-text>
        <v-menu
          v-model="pickerMenu"
          :close-on-content-click="false"
          transition="scale-transition"
          offset-y
          max-width="290px"
          min-width="auto"
        >
          <template #activator="{ on, attrs }">
            <v-text-field
              v-model="newMeal.date"
              label="Date"
              hint="MM/DD/YYYY format"
              persistent-hint
              :prepend-icon="$globals.icons.calendar"
              v-bind="attrs"
              readonly
              v-on="on"
            ></v-text-field>
          </template>
          <v-date-picker v-model="newMeal.date" no-title @input="pickerMenu = false"></v-date-picker>
        </v-menu>
        <v-autocomplete
          v-if="!noteOnly"
          v-model="newMeal.recipeId"
          label="Meal Recipe"
          :items="allRecipes"
          item-text="name"
          item-value="id"
          :return-object="false"
        ></v-autocomplete>
        <template v-else>
          <v-text-field v-model="newMeal.title" label="Meal Title"> </v-text-field>
          <v-textarea v-model="newMeal.text" label="Meal Note"> </v-textarea>
        </template>
      </v-card-text>
      <v-card-actions>
        <v-switch v-model="noteOnly" label="Note Only"></v-switch>
        <v-spacer></v-spacer>
        <BaseButton @click="actions.createOne(newMeal)" />
      </v-card-actions>
    </v-card>

    <div class="d-flex justify-center my-2 align-center" style="gap: 10px">
      <v-btn icon color="info" rounded outlined @click="backOneWeek">
        <v-icon>{{ $globals.icons.back }} </v-icon>
      </v-btn>
      <v-btn rounded outlined readonly style="pointer-events: none">
        {{ $d(weekRange.start, "short") }} - {{ $d(weekRange.end, "short") }}
      </v-btn>
      <v-btn icon color="info" rounded outlined @click="forwardOneWeek">
        <v-icon>{{ $globals.icons.forward }} </v-icon>
      </v-btn>
    </div>
    <!-- <v-row class="mt-2">
      <v-col v-for="(plan, index) in mealsByDate" :key="index">
        <p class="h5 text-center">
          {{ $d(plan.date, "short") }}
        </p>
        <draggable
          tag="div"
          :value="plan.meals"
          group="meals"
          :data-index="index"
          :data-box="plan.date"
          style="min-height: 150px"
          @end="onMoveCallback"
        >
          <v-hover v-for="mealplan in plan.meals" :key="mealplan.id" v-model="hover[mealplan.id]" open-delay="100">
            <RecipeCardMobile
              class="relative my-1 text-center"
              :name="mealplan.recipe.name"
              :slug="mealplan.recipe.slug"
              @selected="() => {}"
            >
              <template #avatar>
                <div />
              </template>
              <template #actions>
                <div />
              </template>
            </RecipeCardMobile>
          </v-hover>
        </draggable>
      </v-col>
    </v-row> -->
    <section>
      <v-card v-for="(plan, index) in mealsByDate" :key="index" flat class="d-flex flex-column align-center mb-4">
        <v-card-title label color="accent" class="headline mr-auto pb-0">
          {{ $d(plan.date, "short") }}
        </v-card-title>
        <v-divider class="my-1"></v-divider>
        <draggable
          tag="div"
          :value="plan.meals"
          group="meals"
          :data-index="index"
          :data-box="plan.date"
          style="min-height: 100px; min-width: 100%"
          class="d-flex flex-wrap"
          @end="onMoveCallback"
        >
          <v-hover v-for="mealplan in plan.meals" :key="mealplan.id" v-model="hover[mealplan.id]" open-delay="100">
            <RecipeCardMobile
              class="relative ma-1"
              style="max-width: 500px"
              :name="mealplan.recipe.name"
              :slug="mealplan.recipe.slug"
              :description="mealplan.recipe.description"
              :rating="mealplan.recipe.rating"
              :image="mealplan.recipe.image"
              @selected="() => {}"
            >
            </RecipeCardMobile>
          </v-hover>
        </draggable>
      </v-card>
    </section>
  </v-container>
</template>
  
<script lang="ts">
import { computed, defineComponent, reactive, toRefs } from "@nuxtjs/composition-api";
import { isSameDay, addDays, subDays, parseISO, format } from "date-fns";
import { SortableEvent } from "sortablejs"; // eslint-disable-line
import draggable from "vuedraggable";
import { useMealplans } from "~/composables/use-group-mealplan";
import { useRecipes, allRecipes } from "~/composables/use-recipes";
import RecipeCardMobile from "~/components/Domain/Recipe/RecipeCardMobile.vue";

export default defineComponent({
  components: {
    draggable,
    RecipeCardMobile,
  },
  setup() {
    const { mealplans, actions } = useMealplans();

    useRecipes(true, true);
    const state = reactive({
      hover: {},
      pickerMenu: null,
      noteOnly: false,
      start: null as Date | null,
      today: new Date(),
      end: null as Date | null,
    });

    function filterMealByDate(date: Date) {
      if (!mealplans.value) return;
      return mealplans.value.filter((meal) => {
        const mealDate = parseISO(meal.date);
        return isSameDay(mealDate, date);
      });
    }

    function forwardOneWeek() {
      if (!state.today) return;
      // @ts-ignore
      state.today = addDays(state.today, +5);
    }

    function backOneWeek() {
      if (!state.today) return;
      // @ts-ignore
      state.today = addDays(state.today, -5);
    }

    function onMoveCallback(evt: SortableEvent) {
      // Adapted From https://github.com/SortableJS/Vue.Draggable/issues/1029
      const ogEvent: DragEvent = (evt as any).originalEvent;

      if (ogEvent && ogEvent.type !== "drop") {
        // The drop was cancelled, unsure if anything needs to be done?
        console.log("Cancel Move Event");
      } else {
        // A Meal was moved, set the new date value and make a update request and refresh the meals
        const fromMealsByIndex = evt.from.getAttribute("data-index");
        const toMealsByIndex = evt.to.getAttribute("data-index");

        if (fromMealsByIndex) {
          // @ts-ignore
          const mealData = mealsByDate.value[fromMealsByIndex].meals[evt.oldIndex as number];
          // @ts-ignore
          const destDate = mealsByDate.value[toMealsByIndex].date;

          console.log({ destDate });
          mealData.date = format(destDate, "yyyy-MM-dd");

          actions.updateOne(mealData);
        }
      }
    }

    const mealsByDate = computed(() => {
      return days.value.map((day) => {
        return { date: day, meals: filterMealByDate(day as any) };
      });
    });

    const weekRange = computed(() => {
      // @ts-ignore - Not Sure Why This is not working
      const end = addDays(state.today, 2);
      // @ts-ignore - Not sure why the type is invalid
      const start = subDays(state.today, 2);
      return { start, end, today: state.today };
    });

    const days = computed(() => {
      if (weekRange.value?.start === null) return [];
      return Array.from(Array(5).keys()).map(
        // @ts-ignore
        (i) => new Date(weekRange.value.start.getTime() + i * 24 * 60 * 60 * 1000)
      );
    });

    const newMeal = reactive({
      date: null,
      title: "",
      text: "",
      recipeId: null,
    });

    return {
      mealplans,
      actions,
      newMeal,
      allRecipes,
      ...toRefs(state),
      mealsByDate,
      onMoveCallback,
      backOneWeek,
      forwardOneWeek,
      weekRange,
      days,
    };
  },
});
</script>
  