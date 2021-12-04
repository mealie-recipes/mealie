<template>
  <v-container>
    <!-- Create Meal Dialog -->
    <BaseDialog
      v-model="createMealDialog"
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
          <v-select v-model="newMeal.entryType" :return-object="false" :items="planTypeOptions" label="Entry Type">
          </v-select>

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
    <v-row class="">
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
        <v-sheet class="mb-2 bottom-color-border">
          <p class="headline text-center mb-1">
            {{ $d(plan.date, "short") }}
          </p>
        </v-sheet>

        <!-- Day Column Recipes -->
        <template v-if="edit">
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
              <v-list-item :to="edit || !mealplan.recipe ? null : `/recipe/${mealplan.recipe.slug}`">
                <v-list-item-avatar :rounded="false">
                  <RecipeCardImage
                    v-if="mealplan.recipe"
                    tiny
                    icon-size="25"
                    :slug="mealplan.recipe ? mealplan.recipe.slug : ''"
                  />
                  <v-icon v-else>
                    {{ $globals.icons.primary }}
                  </v-icon>
                </v-list-item-avatar>
                <v-list-item-content>
                  <v-list-item-title class="mb-1">
                    {{ mealplan.recipe ? mealplan.recipe.name : mealplan.title }}
                  </v-list-item-title>
                  <v-list-item-subtitle style="min-height: 16px">
                    {{ mealplan.recipe ? mealplan.recipe.description + " " : mealplan.text }}
                  </v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-divider class="mx-2"></v-divider>
              <div class="py-2 px-2 d-flex">
                <v-menu offset-y>
                  <template #activator="{ on, attrs }">
                    <v-chip v-bind="attrs" label small color="accent" v-on="on" @click.prevent>
                      <v-icon left>
                        {{ $globals.icons.tags }}
                      </v-icon>
                      {{ mealplan.entryType }}
                    </v-chip>
                  </template>
                  <v-list>
                    <v-list-item
                      v-for="mealType in planTypeOptions"
                      :key="mealType.value"
                      @click="actions.setType(mealplan, mealType.value)"
                    >
                      <v-list-item-title> {{ mealType.text }} </v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-menu>
                <v-spacer></v-spacer>
                <v-btn color="info" class="mr-2" small icon>
                  <v-icon>{{ $globals.icons.cartCheck }}</v-icon>
                </v-btn>
                <v-btn color="error" small icon @click="actions.deleteOne(mealplan.id)">
                  <v-icon>{{ $globals.icons.delete }}</v-icon>
                </v-btn>
              </div>
            </v-card>
          </draggable>

          <!-- Day Column Actions -->
          <v-card outlined class="mt-auto">
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
        </template>
        <template v-else-if="plan.meals">
          <RecipeCard
            v-for="mealplan in plan.meals"
            :key="mealplan.id"
            :recipe-id="0"
            :image-height="125"
            class="mb-2"
            :route="mealplan.recipe ? true : false"
            :slug="mealplan.recipe ? mealplan.recipe.slug : mealplan.title"
            :description="mealplan.recipe ? mealplan.recipe.description : mealplan.text"
            :name="mealplan.recipe ? mealplan.recipe.name : mealplan.title"
          >
            <template #actions>
              <v-divider class="mb-0 mt-2 mx-2"></v-divider>
              <v-card-actions class="justify-end mt-1">
                <v-chip label small color="accent">
                  <v-icon left>
                    {{ $globals.icons.tags }}
                  </v-icon>
                  {{ mealplan.entryType }}
                </v-chip>
              </v-card-actions>
            </template>
          </RecipeCard>
        </template>

        <v-skeleton-loader v-else elevation="2" type="image, list-item-two-line"></v-skeleton-loader>
      </v-col>
    </v-row>
  </v-container>
</template>
  
<script lang="ts">
import { computed, defineComponent, reactive, toRefs, watch } from "@nuxtjs/composition-api";
import { isSameDay, addDays, subDays, parseISO, format } from "date-fns";
import { SortableEvent } from "sortablejs"; // eslint-disable-line
import draggable from "vuedraggable";
import { useMealplans, planTypeOptions } from "~/composables/use-group-mealplan";
import { useRecipes, allRecipes } from "~/composables/recipes";
import RecipeCardImage from "~/components/Domain/Recipe/RecipeCardImage.vue";
import RecipeCard from "~/components/Domain/Recipe/RecipeCard.vue";

export default defineComponent({
  components: {
    draggable,
    RecipeCardImage,
    RecipeCard,
  },
  setup() {
    const { mealplans, actions, loading } = useMealplans();

    useRecipes(true, true);
    const state = reactive({
      createMealDialog: false,
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
      recipeId: null as Number | null,
      entryType: "dinner",
    });

    function openDialog(date: Date) {
      newMeal.date = format(date, "yyyy-MM-dd");
      // @ts-ignore
      state.createMealDialog = true;
    }

    function resetDialog() {
      newMeal.date = "";
      newMeal.title = "";
      newMeal.text = "";
      newMeal.entryType = "dinner";
      newMeal.recipeId = null;
    }

    async function randomMeal(date: Date) {
      // TODO: Refactor to use API call to get random recipe
      // @ts-ignore
      const randomRecipe = allRecipes.value[Math.floor(Math.random() * allRecipes.value.length)];

      newMeal.date = format(date, "yyyy-MM-dd");

      newMeal.recipeId = randomRecipe.id || null;

      console.log(newMeal.recipeId, randomRecipe.id);

      // @ts-ignore
      await actions.createOne({ ...newMeal });
      resetDialog();
    }

    return {
      ...toRefs(state),
      actions,
      allRecipes,
      backOneWeek,
      days,
      dialog,
      forwardOneWeek,
      loading,
      mealplans,
      mealsByDate,
      newMeal,
      onMoveCallback,
      openDialog,
      planTypeOptions,
      randomMeal,
      resetDialog,
      weekRange,
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
.left-color-border {
  border-left: 5px solid var(--v-primary-base) !important;
}

.bottom-color-border {
  border-bottom: 2px solid var(--v-primary-base) !important;
}
</style>
  