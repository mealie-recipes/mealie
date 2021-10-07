<template>
  <v-container>
    <!-- Create Meal Dialog -->
    <BaseDialog
      ref="domMealDialog"
      :title="$t('meal-plan.create-a-new-meal-plan')"
      color="primary"
      :icon="$globals.icons.foods"
      @submit="
        actions.createOne(newMeal);
        resetDialog();
      "
    >
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
        <v-card-text>
          <v-autocomplete
            v-if="!dialog.note"
            v-model="newMeal.recipeId"
            label="Meal Recipe"
            :items="allRecipes"
            item-text="name"
            item-value="id"
            :return-object="false"
          ></v-autocomplete>
          <template v-else>
            <v-text-field v-model="newMeal.title" label="Meal Title"> </v-text-field>
            <v-textarea v-model="newMeal.text" rows="2" label="Meal Note"> </v-textarea>
          </template>
        </v-card-text>
        <v-card-actions class="my-0 py-0">
          <v-switch v-model="dialog.note" class="mt-n3" label="Note Only"></v-switch>
        </v-card-actions>
      </v-card-text>
    </BaseDialog>

    <!-- Date Forward / Back -->
    <div class="d-flex justify-center flex-column">
      <h3 class="text-h6 mt-2 text-center">{{ $d(weekRange.start, "short") }} - {{ $d(weekRange.end, "short") }}</h3>
      <div class="d-flex justify-center my-2 align-center" style="gap: 10px">
        <v-btn icon color="info" outlined @click="backOneWeek">
          <v-icon>{{ $globals.icons.back }} </v-icon>
        </v-btn>
        <v-btn icon color="info" outlined @click="forwardOneWeek">
          <v-icon>{{ $globals.icons.forward }} </v-icon>
        </v-btn>
      </div>
    </div>
    <v-switch v-model="edit" label="Editor"></v-switch>
    <v-row class="mt-2">
      <v-col
        v-for="(plan, index) in mealsByDate"
        :key="index"
        cols="12"
        sm="12"
        md="4"
        lg="3"
        xl="2"
        class="col-borders my-1 d-flex flex-column"
      >
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
          <v-card v-for="mealplan in plan.meals" :key="mealplan.id" v-model="hover[mealplan.id]" class="my-1">
            <v-list-item>
              <v-list-item-avatar :rounded="false">
                <RecipeCardImage v-if="mealplan.recipe" tiny icon-size="25" :slug="mealplan.recipe.slug" />
                <v-icon v-else>
                  {{ $globals.icons.primary }}
                </v-icon>
              </v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title class="mb-1">
                  {{ mealplan.recipe ? mealplan.recipe.name : mealplan.title }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ mealplan.recipe ? mealplan.recipe.description : mealplan.text }}
                </v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
            <v-divider class="mx-2"></v-divider>
            <v-card-actions>
              <v-btn color="error" icon @click="actions.deleteOne(mealplan.id)">
                <v-icon>{{ $globals.icons.delete }}</v-icon>
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn
                v-if="mealplan.recipe"
                color="info"
                icon
                nuxt
                target="_blank"
                :to="`/recipe/${mealplan.recipe.slug}`"
              >
                <v-icon>{{ $globals.icons.openInNew }}</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </draggable>
        <v-card v-if="edit" outlined class="mt-auto">
          <v-card-actions class="d-flex">
            <div style="width: 50%">
              <v-btn block text @click="randomMeal(plan.date)">
                <v-icon large>{{ $globals.icons.diceMultiple }}</v-icon>
              </v-btn>
            </div>
            <div style="width: 50%">
              <v-btn block text @click="openDialog(plan.date)">
                <v-icon large>{{ $globals.icons.createAlt }}</v-icon>
              </v-btn>
            </div>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>
  
<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from "@nuxtjs/composition-api";
import { isSameDay, addDays, subDays, parseISO, format } from "date-fns";
import { SortableEvent } from "sortablejs"; // eslint-disable-line
import draggable from "vuedraggable";
import { useMealplans } from "~/composables/use-group-mealplan";
import { useRecipes, allRecipes } from "~/composables/use-recipes";
import RecipeCardImage from "~/components/Domain/Recipe/RecipeCardImage.vue";

export default defineComponent({
  components: {
    draggable,
    RecipeCardImage,
  },
  setup() {
    const { mealplans, actions } = useMealplans();

    useRecipes(true, true);
    const state = reactive({
      edit: false,
      hover: {},
      pickerMenu: null,
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
      const end = addDays(state.today, 6);
      // @ts-ignore - Not sure why the type is invalid
      const start = subDays(state.today, 1);
      return { start, end, today: state.today };
    });

    const days = computed(() => {
      if (weekRange.value?.start === null) return [];
      return Array.from(Array(8).keys()).map(
        // @ts-ignore
        (i) => new Date(weekRange.value.start.getTime() + i * 24 * 60 * 60 * 1000)
      );
    });

    // =====================================================
    // New Meal Dialog
    const domMealDialog = ref(null);
    const dialog = reactive({
      loading: false,
      error: false,
      note: false,
    });

    watch(dialog, () => {
      if (dialog.note) {
        newMeal.recipeId = null;
      }
      newMeal.title = "";
      newMeal.text = "";
    });
    const newMeal = reactive({
      date: "",
      title: "",
      text: "",
      recipeId: null,
    });

    function openDialog(date: Date) {
      newMeal.date = format(date, "yyyy-MM-dd");
      // @ts-ignore
      domMealDialog.value.open();
    }

    function resetDialog() {
      newMeal.date = "";
      newMeal.title = "";
      newMeal.text = "";
      newMeal.recipeId = null;
    }

    function randomMeal(date: Date) {
      // TODO: Refactor to use API call to get random recipe
      // @ts-ignore
      const randomRecipe = allRecipes.value[Math.floor(Math.random() * allRecipes.value.length)];

      newMeal.date = format(date, "yyyy-MM-dd");
      // @ts-ignore
      newMeal.recipeId = randomRecipe.id;

      // @ts-ignore
      actions.createOne(newMeal);
      resetDialog();
    }

    return {
      resetDialog,
      randomMeal,
      dialog,
      domMealDialog,
      openDialog,
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
  head() {
    return {
      title: this.$t("meal-plan.dinner-this-week") as string,
    };
  },
});
</script>

<style lang="css">
.col-borders {
  border-top: 1px solid #e0e0e0;
}
</style>
  