<template>
  <v-container>
    <!-- Create Meal Dialog -->
    <BaseDialog
      v-model="createMealDialog"
      :title="$tc('meal-plan.create-a-new-meal-plan')"
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
              :label="$t('general.date')"
              :hint="$t('recipe.date-format-hint-yyyy-mm-dd')"
              persistent-hint
              :prepend-icon="$globals.icons.calendar"
              v-bind="attrs"
              readonly
              v-on="on"
            ></v-text-field>
          </template>
          <v-date-picker
            v-model="newMeal.date"
            :first-day-of-week="firstDayOfWeek"
            no-title
            @input="pickerMenu = false"
          ></v-date-picker>
        </v-menu>
        <v-card-text>
          <v-select
            v-model="newMeal.entryType"
            :return-object="false"
            :items="planTypeOptions"
            :label="$t('recipe.entry-type')"
          >
          </v-select>

          <v-autocomplete
            v-if="!dialog.note"
            v-model="newMeal.recipeId"
            :label="$t('meal-plan.meal-recipe')"
            :items="recipeResults"
            :loading="loadingRecipes"
            :search-input.sync="recipeSearchTerm"
            cache-items
            item-text="name"
            item-value="id"
            :return-object="false"
          ></v-autocomplete>
          <template v-else>
            <v-text-field v-model="newMeal.title" :label="$t('meal-plan.meal-title')"> </v-text-field>
            <v-textarea v-model="newMeal.text" rows="2" :label="$t('meal-plan.meal-note')"> </v-textarea>
          </template>
        </v-card-text>
        <v-card-actions class="my-0 py-0">
          <v-switch v-model="dialog.note" class="mt-n3" :label="$t('meal-plan.note-only')"></v-switch>
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
    <div class="d-flex align-center justify-space-between">
      <v-switch v-model="edit" :label="$t('meal-plan.editor')"></v-switch>
      <ButtonLink :icon="$globals.icons.calendar" to="/group/mealplan/settings" :text="$tc('general.settings')" />
    </div>
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
            handle=".handle"
            :value="plan.meals"
            group="meals"
            :data-index="index"
            :data-box="plan.date"
            style="min-height: 150px"
            @end="onMoveCallback"
          >
            <v-card
              v-for="mealplan in plan.meals"
              :key="mealplan.id"
              v-model="hover[mealplan.id]"
              class="my-1"
              :class="{ handle: $vuetify.breakpoint.smAndUp }"
            >
              <v-list-item :to="edit || !mealplan.recipe ? null : `/recipe/${mealplan.recipe.slug}`">
                <v-list-item-avatar :rounded="false">
                  <RecipeCardImage
                    v-if="mealplan.recipe"
                    :recipe-id="mealplan.recipe.id"
                    tiny
                    icon-size="25"
                    :slug="mealplan.recipe ? mealplan.recipe.slug : ''"
                  >
                  </RecipeCardImage>
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
              <div class="py-2 px-2 d-flex" style="align-items: center">
                <v-btn small icon :class="{ handle: !$vuetify.breakpoint.smAndUp }">
                  <v-icon>
                    {{ $globals.icons.arrowUpDown }}
                  </v-icon>
                </v-btn>

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

                <v-btn class="ml-auto" small icon @click="actions.deleteOne(mealplan.id)">
                  <v-icon>{{ $globals.icons.delete }}</v-icon>
                </v-btn>
              </div>
            </v-card>
          </draggable>

          <!-- Day Column Actions -->
          <div class="d-flex justify-end">
            <BaseButtonGroup
              :buttons="[
                {
                  icon: $globals.icons.diceMultiple,
                  text: $tc('meal-plan.random-meal'),
                  event: 'random',
                  children: [
                    {
                      icon: $globals.icons.diceMultiple,
                      text: 'Breakfast',
                      event: 'randomBreakfast',
                    },

                    {
                      icon: $globals.icons.diceMultiple,
                      text: $tc('meal-plan.lunch'),
                      event: 'randomLunch',
                    },
                  ],
                },
                {
                  icon: $globals.icons.potSteam,
                  text: $tc('meal-plan.random-dinner'),
                  event: 'randomDinner',
                },
                {
                  icon: $globals.icons.bowlMixOutline,
                  text: $tc('meal-plan.random-side'),
                  event: 'randomSide',
                },
                {
                  icon: $globals.icons.createAlt,
                  text: $tc('general.new'),
                  event: 'create',
                },
              ]"
              @create="openDialog(plan.date)"
              @randomBreakfast="randomMeal(plan.date, 'breakfast')"
              @randomLunch="randomMeal(plan.date, 'lunch')"
              @randomDinner="randomMeal(plan.date, 'dinner')"
              @randomSide="randomMeal(plan.date, 'side')"
            />
          </div>
        </template>
        <template v-else-if="plan.meals">
          <RecipeCard
            v-for="mealplan in plan.meals"
            :key="mealplan.id"
            :recipe-id="mealplan.recipe ? mealplan.recipe.id : ''"
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
                <RecipeContextMenu
                  :name="mealplan.recipe ? mealplan.recipe.name : mealplan.title"
                  :recipe-id="mealplan.recipe ? mealplan.recipe.id : ''"
                  :slug="mealplan.recipe ? mealplan.recipe.slug : ''"
                  :use-items="{
                    delete: false,
                    edit: false,
                    download: true,
                    duplicate: false,
                    mealplanner: false,
                    print: true,
                    printPreferences: false,
                    share: false,
                    shoppingList: true,
                    publicUrl: false,
                  }"
                />
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
import { computed, defineComponent, reactive, ref, toRefs, watch } from "@nuxtjs/composition-api";
import { isSameDay, addDays, subDays, parseISO, format } from "date-fns";
import { SortableEvent } from "sortablejs";
import draggable from "vuedraggable";
import { watchDebounced } from "@vueuse/core";
import { useMealplans, planTypeOptions } from "~/composables/use-group-mealplan";
import RecipeCardImage from "~/components/Domain/Recipe/RecipeCardImage.vue";
import RecipeCard from "~/components/Domain/Recipe/RecipeCard.vue";
import RecipeContextMenu from "~/components/Domain/Recipe/RecipeContextMenu.vue";
import { PlanEntryType } from "~/lib/api/types/meal-plan";
import { useUserApi } from "~/composables/api";
import { useGroupSelf } from "~/composables/use-groups";
import { RecipeSummary } from "~/lib/api/types/recipe";

export default defineComponent({
  components: {
    draggable,
    RecipeCardImage,
    RecipeCard,
    RecipeContextMenu,
  },
  setup() {
    const state = reactive({
      createMealDialog: false,
      edit: false,
      hover: {} as Record<string, boolean>,
      pickerMenu: null,
      today: new Date(),
      recipeResults: [] as RecipeSummary[],
      loadingRecipes: false,
    });
    const recipeSearchTerm = ref("");

    const weekRange = computed(() => {
      return {
        start: subDays(state.today as Date, 1),
        end: addDays(state.today as Date, 6),
      };
    });

    const api = useUserApi();

    const { mealplans, actions, loading } = useMealplans(weekRange);

    async function searchRecipes(term: string) {
      state.loadingRecipes = true;
      const { data, error } = await api.recipes.search({
        search: term,
        page: 1,
        orderBy: "name",
        orderDirection: "asc",
        perPage: 20,
      });

      if (error) {
        console.error(error);
        state.loadingRecipes = false;
        state.recipeResults = [];
        return;
      }

      if (data) {
        state.recipeResults = data.items;
      }

      state.loadingRecipes = false;
    }

    watchDebounced(
      recipeSearchTerm,
      async (term: string) => {
        await searchRecipes(term);
      },
      { debounce: 500 }
    );

    const { group } = useGroupSelf();

    const firstDayOfWeek = computed(() => {
      const pref = group.value?.preferences?.firstDayOfWeek;

      if (pref) {
        return pref;
      }

      return 0;
    });

    function filterMealByDate(date: Date) {
      if (!mealplans.value) return [];
      return mealplans.value.filter((meal) => {
        const mealDate = parseISO(meal.date);
        return isSameDay(mealDate, date);
      });
    }

    function forwardOneWeek() {
      if (!state.today) return;
      state.today = addDays(state.today as Date, +5);
    }

    function backOneWeek() {
      if (!state.today) return;
      state.today = addDays(state.today as Date, -5);
    }

    function onMoveCallback(evt: SortableEvent) {
      const supportedEvents = ["drop", "touchend"];

      // Adapted From https://github.com/SortableJS/Vue.Draggable/issues/1029
      const ogEvent: DragEvent = (evt as any).originalEvent;

      if (ogEvent && ogEvent.type in supportedEvents) {
        // The drop was cancelled, unsure if anything needs to be done?
        console.log("Cancel Move Event");
      } else {
        // A Meal was moved, set the new date value and make an update request and refresh the meals
        const fromMealsByIndex = parseInt(evt.from.getAttribute("data-index") ?? "");
        const toMealsByIndex = parseInt(evt.to.getAttribute("data-index") ?? "");

        if (!isNaN(fromMealsByIndex) && !isNaN(toMealsByIndex)) {
          const mealData = mealsByDate.value[fromMealsByIndex].meals[evt.oldIndex as number];
          const destDate = mealsByDate.value[toMealsByIndex].date;

          mealData.date = format(destDate, "yyyy-MM-dd");

          actions.updateOne(mealData);
        }
      }
    }

    const mealsByDate = computed(() => {
      return days.value.map((day) => {
        return { date: day, meals: filterMealByDate(day) };
      });
    });

    const days = computed(() => {
      return Array.from(Array(8).keys()).map(
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
        newMeal.recipeId = undefined;
      }
      newMeal.title = "";
      newMeal.text = "";
    });

    const newMeal = reactive({
      date: "",
      title: "",
      text: "",
      recipeId: undefined as string | undefined,
      entryType: "dinner" as PlanEntryType,
    });

    function openDialog(date: Date) {
      newMeal.date = format(date, "yyyy-MM-dd");
      state.createMealDialog = true;
    }

    function resetDialog() {
      newMeal.date = "";
      newMeal.title = "";
      newMeal.text = "";
      newMeal.entryType = "dinner";
      newMeal.recipeId = undefined;
    }

    async function randomMeal(date: Date, type: PlanEntryType) {
      const { data } = await api.mealplans.setRandom({
        date: format(date, "yyyy-MM-dd"),
        entryType: type,
      });

      if (data) {
        actions.refreshAll();
      }
    }

    return {
      ...toRefs(state),
      actions,
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
      firstDayOfWeek,
      recipeSearchTerm,
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
