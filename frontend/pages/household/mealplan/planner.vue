<template>
  <v-container>
    <RecipeDialogAddToShoppingList
      v-if="shoppingLists"
      v-model="state.shoppingListDialog"
      :recipes="weekRecipesWithScales"
      :shopping-lists="shoppingLists"
    />
    <v-menu
      v-model="state.picker"
      :close-on-content-click="false"
      transition="scale-transition"
      offset-y
      min-width="auto"
    >
      <template #activator="{ props }">
        <v-btn
          color="primary"
          class="mb-2"
          v-bind="props"
        >
          <v-icon start>
            {{ $globals.icons.calendar }}
          </v-icon>
          {{ $d(weekRange.start, "short") }} - {{ $d(weekRange.end, "short") }}
        </v-btn>
      </template>

      <v-card>
        <v-date-picker
          v-model="state.range"
          hide-header
          :multiple="'range'"
          :first-day-of-week="firstDayOfWeek"
          :local="$i18n.locale"
        />

        <v-card-text>
          <v-number-input
            v-model="numberOfDays"
            :min="1"
            control-variant="stacked"
            inset
            :label="$t('meal-plan.numberOfDays-label')"
            :hint="$t('meal-plan.numberOfDays-hint')"
            persistent-hint
          />
        </v-card-text>
      </v-card>
    </v-menu>

    <div class="d-flex flex-wrap align-center justify-space-between mb-2">
      <v-tabs style="width: fit-content;">
        <v-tab :to="{ name: TABS.view, query: route.query }">
          {{ $t('meal-plan.meal-planner') }}
        </v-tab>
        <v-tab :to="{ name: TABS.edit, query: route.query }">
          {{ $t('general.edit') }}
        </v-tab>
      </v-tabs>
      <BaseButton
        v-if="route.name === TABS.view"
        color="info"
        :icon="$globals.icons.cartCheck"
        :text="$t('meal-plan.add-all-to-list')"
        :disabled="!hasRecipes"
        :loading="state.addAllLoading"
        class="ml-auto mr-4"
        @click="addAllToList"
      />
      <ButtonLink
        :icon="$globals.icons.calendar"
        :to="`/household/mealplan/settings`"
        :text="$t('general.settings')"
      />
    </div>

    <div>
      <NuxtPage
        :mealplans="mealsByDate"
        :actions="actions"
      />
    </div>

    <v-row />
  </v-container>
</template>

<script lang="ts">
import { isSameDay, addDays, parseISO, format, isValid } from "date-fns";
import RecipeDialogAddToShoppingList from "~/components/Domain/Recipe/RecipeDialogAddToShoppingList.vue";
import { useHouseholdSelf } from "~/composables/use-households";
import { useMealplans } from "~/composables/use-group-mealplan";
import { useUserMealPlanPreferences } from "~/composables/use-users/preferences";
import type { ShoppingListSummary } from "~/lib/api/types/household";
import { useUserApi } from "~/composables/api";

export default defineNuxtComponent({
  components: {
    RecipeDialogAddToShoppingList,
  },
  setup() {
    const TABS = {
      view: "household-mealplan-planner-view",
      edit: "household-mealplan-planner-edit",
    };

    const route = useRoute();
    const router = useRouter();
    const i18n = useI18n();
    const api = useUserApi();
    const { household } = useHouseholdSelf();

    useSeoMeta({
      title: i18n.t("meal-plan.dinner-this-week"),
    });

    const mealPlanPreferences = useUserMealPlanPreferences();
    const numberOfDays = ref<number>(mealPlanPreferences.value.numberOfDays || 7);
    watch(numberOfDays, (val) => {
      mealPlanPreferences.value.numberOfDays = Number(val);
    });

    // Force to /view if current route is /planner
    if (route.path === "/household/mealplan/planner") {
      router.push({
        name: TABS.view,
        query: route.query,
      });
    }

    function safeParseISO(date: string, fallback: Date | undefined = undefined) {
      try {
        const parsed = parseISO(date);
        return isValid(parsed) ? parsed : fallback;
      }
      catch {
        return fallback;
      }
    }

    // Initialize dates from query parameters or defaults
    const initialStartDate = safeParseISO(route.query.start as string, new Date());
    const initialEndDate = safeParseISO(route.query.end as string, addDays(new Date(), adjustForToday(numberOfDays.value)));

    const state = ref({
      range: [initialStartDate, initialEndDate] as [Date, Date],
      start: initialStartDate,
      picker: false,
      end: initialEndDate,
      shoppingListDialog: false,
      addAllLoading: false,
    });

    const shoppingLists = ref<ShoppingListSummary[]>();

    const firstDayOfWeek = computed(() => {
      return household.value?.preferences?.firstDayOfWeek || 0;
    });

    const weekRange = computed(() => {
      const sorted = [...state.value.range].sort((a, b) => a.getTime() - b.getTime());

      const start = sorted[0];
      const end = sorted[sorted.length - 1];

      if (start && end) {
        return { start, end };
      }
      return {
        start: new Date(),
        end: addDays(new Date(), adjustForToday(numberOfDays.value)),
      };
    });

    // Update query parameters when date range changes
    watch(weekRange, (newRange) => {
      // Keep current route name and params, just update the query
      router.replace({
        name: route.name || TABS.view,
        params: route.params,
        query: {
          ...route.query,
          start: format(newRange.start, "yyyy-MM-dd"),
          end: format(newRange.end, "yyyy-MM-dd"),
        },
      });
    }, { immediate: true });

    const { mealplans, actions } = useMealplans(weekRange);

    function filterMealByDate(date: Date) {
      if (!mealplans.value) return [];
      return mealplans.value.filter((meal) => {
        const mealDate = parseISO(meal.date);
        return isSameDay(mealDate, date);
      });
    }

    function adjustForToday(days: number) {
      // The use case for this function is "how many days are we adding to 'today'?"
      // e.g. If the user wants 7 days, we substract one to do "today + 6"
      return days > 0 ? days - 1 : days + 1;
    }

    const days = computed(() => {
      const numDays
        = Math.floor((weekRange.value.end.getTime() - weekRange.value.start.getTime()) / (1000 * 60 * 60 * 24)) + 1;

      // Calculate absolute value
      if (numDays < 0) return [];

      return Array.from(Array(numDays).keys()).map(
        (i) => {
          const date = new Date(weekRange.value.start.getTime());
          date.setDate(date.getDate() + i);
          return date;
        },
      );
    });

    const mealsByDate = computed(() => {
      return days.value.map((day) => {
        return { date: day, meals: filterMealByDate(day) };
      });
    });

    const hasRecipes = computed(() => {
      return mealsByDate.value.some(day => day.meals.some(meal => meal.recipe));
    });

    const weekRecipesWithScales = computed(() => {
      const allRecipes: any[] = [];
      for (const day of mealsByDate.value) {
        for (const meal of day.meals) {
          if (meal.recipe) {
            allRecipes.push(meal.recipe);
          }
        }
      }
      return allRecipes.map(recipe => ({
        scale: 1,
        ...recipe,
      }));
    });

    async function getShoppingLists() {
      const { data } = await api.shopping.lists.getAll(1, -1, { orderBy: "name", orderDirection: "asc" });
      if (data) {
        shoppingLists.value = data.items as ShoppingListSummary[] ?? [];
      }
    }

    async function addAllToList() {
      state.value.addAllLoading = true;
      await getShoppingLists();
      state.value.shoppingListDialog = true;
      state.value.addAllLoading = false;
    }

    return {
      TABS,
      route,
      state,
      actions,
      mealsByDate,
      weekRange,
      firstDayOfWeek,
      numberOfDays,
      hasRecipes,
      shoppingLists,
      weekRecipesWithScales,
      addAllToList,
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
