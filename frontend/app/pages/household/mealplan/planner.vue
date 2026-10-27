<template>
  <v-container>
    <RecipeDialogAddToShoppingList
      v-if="shoppingLists"
      v-model="shoppingListDialog"
      :recipes="weekRecipesWithScales"
      :shopping-lists="shoppingLists"
      @list-created="addShoppingList"
    />
    <GroupMealPlanCalendarDialog v-model="calendarDialog" />
    <!-- range navigation and page actions share one toolbar, kept apart from the plan below -->
    <div class="d-flex flex-wrap align-center ga-2">
      <v-btn :icon="$globals.icons.chevronLeft" flat rounded="md" density="comfortable" @click="() => changeWeek(-1)" />
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
            v-bind="props"
          >
            <v-icon start>
              {{ $globals.icons.calendar }}
            </v-icon>
            {{ $d(weekRange.start, "short") }} - {{ $d(weekRange.end, "short") }}
          </v-btn>
        </template>

        <v-card>
          <MealPlanDatePicker
            v-model="state.range"
            hide-header
            :multiple="'range'"
            :first-day-of-week="firstDayOfWeek"
            :local="$i18n.locale"
          />

          <v-card-text>
            <v-number-input
              v-model="numberOfWeeksPast"
              :min="0"
              inset
              :label="$t('meal-plan.numberOfWeeksPast-label')"
              :hint="$t('meal-plan.numberOfWeeksPast-hint')"
              persistent-hint
            />
          </v-card-text>

          <v-card-text>
            <v-number-input
              v-model="numberOfWeeks"
              :min="1"
              inset
              :label="$t('meal-plan.numberOfWeeks-label')"
              :hint="$t('meal-plan.numberOfWeeks-hint')"
              persistent-hint
            />
          </v-card-text>
        </v-card>
      </v-menu>
      <v-btn :icon="$globals.icons.chevronRight" flat rounded="md" density="comfortable" @click="() => changeWeek(1)" />
      <BaseButtonGroup
        class="d-flex ms-auto"
        :buttons="[
          edit ? {
            icon: $globals.icons.calendar,
            text: $t('general.view'),
            event: 'view',
          } : {
            icon: $globals.icons.edit,
            text: $t('general.edit'),
            event: 'edit',
          },
          {
            icon: $globals.icons.dotsVertical,
            text: '',
            event: 'three-dot',
            children: [
              {
                icon: $globals.icons.cartCheck,
                text: $t('meal-plan.add-all-to-list'),
                event: 'add-to-list',
                disabled: !hasRecipes,
              },
              {
                icon: $globals.icons.calendar,
                text: $t('meal-plan.calendar-feed'),
                event: 'calendar-feed',
              },
              {
                icon: $globals.icons.cog,
                text: $t('general.settings'),
                event: 'settings',
              },
            ],
          },
        ]"
        @add-to-list="addAllToList"
        @edit="router.push({ name: TABS.edit, query: route.query })"
        @view="router.push({ name: TABS.view, query: route.query })"
        @settings="router.push('/household/mealplan/settings')"
        @calendar-feed="calendarDialog = true"
      />
    </div>
    <v-divider class="my-4" />
    <div>
      <NuxtPage
        :mealplans="plans"
        :actions="actions"
      />
    </div>

    <v-row />
  </v-container>
</template>

<script setup lang="ts">
import { addDays, addWeeks, differenceInCalendarDays, format, isSameDay, isValid, parseISO } from "date-fns";
import GroupMealPlanCalendarDialog from "~/components/Domain/Household/GroupMealPlanCalendarDialog.vue";
import RecipeDialogAddToShoppingList from "~/components/Domain/Recipe/RecipeDialogAddToShoppingList.vue";
import { useAddToShoppingListDialog } from "~/composables/shopping-list-page/use-add-to-shopping-list-dialog";
import type { MealsByDate } from "~/composables/use-group-mealplan";
import { getScaledRecipes, getWeekRange, useMealplans } from "~/composables/use-group-mealplan";
import { useHouseholdSelf } from "~/composables/use-households";
import { useUserMealPlanPreferences } from "~/composables/use-users/preferences";

definePageMeta({
  middleware: ["auth"],
});

const TABS = {
  view: "household-mealplan-planner-view",
  edit: "household-mealplan-planner-edit",
};

const route = useRoute();
const router = useRouter();
const i18n = useI18n();
const { household, actions: householdActions } = useHouseholdSelf();
const { shoppingLists, open: shoppingListDialog, addAllToList, addShoppingList } = useAddToShoppingListDialog();
const calendarDialog = ref(false);

useSeoMeta({
  title: i18n.t("meal-plan.dinner-this-week"),
});

// useHouseholdSelf() caches data in a module-level singleton for the lifetime of the tab,
// so revisiting this page via client-side navigation can otherwise use a stale
// firstDayOfWeek value if household preferences were changed elsewhere (e.g. Admin
// Households panel) in the same session. Force a revalidation whenever this page is entered.
onMounted(() => {
  householdActions.refresh();
});

const mealPlanPreferences = useUserMealPlanPreferences();
const numberOfWeeksPast = ref<number>(mealPlanPreferences.value.numberOfWeeksPast || 0);
const numberOfWeeks = ref<number>(mealPlanPreferences.value.numberOfWeeks || 1);
watch(numberOfWeeksPast, (val) => {
  mealPlanPreferences.value.numberOfWeeksPast = Number(val);
});
watch(numberOfWeeks, (val) => {
  mealPlanPreferences.value.numberOfWeeks = Number(val);
});

// Force to /view if current route is /planner
if (route.path === "/household/mealplan/planner") {
  router.push({
    name: TABS.view,
    query: route.query,
  });
}

const edit = computed(() => {
  return route.path.startsWith("/household/mealplan/planner/edit");
});

function safeParseISO(date: string, fallback: Date | undefined = undefined) {
  try {
    const parsed = parseISO(date);
    return isValid(parsed) ? parsed : fallback;
  }
  catch {
    return fallback;
  }
}

// A day in the first and last week of the default range; `weekRange` rounds them out to whole weeks
function defaultStartDate() {
  return addWeeks(new Date(), -numberOfWeeksPast.value);
}

function defaultEndDate() {
  return addWeeks(new Date(), numberOfWeeks.value - 1);
}

// Initialize dates from query parameters or defaults
const initialStartDate = safeParseISO(route.query.start as string, defaultStartDate());
const initialEndDate = safeParseISO(route.query.end as string, defaultEndDate());

const state = ref({
  range: [initialStartDate, initialEndDate] as [Date, Date],
  start: initialStartDate,
  picker: false,
  end: initialEndDate,
});

const firstDayOfWeek = computed(() => {
  return household.value?.preferences?.firstDayOfWeek || 0;
});

function changeWeek(step: number) {
  const { start, end } = weekRange.value;
  const stepSize = differenceInCalendarDays(end, start) + 1;
  state.value.range = [
    addDays(start, step * stepSize),
    addDays(end, step * stepSize),
  ];
}

// The planner always shows whole weeks, so the selected range is rounded out to the weeks it touches
const weekRange = computed(() => {
  const sorted = [...state.value.range].sort((a, b) => a.getTime() - b.getTime());

  const start = sorted[0] ?? defaultStartDate();
  const end = sorted[sorted.length - 1] ?? defaultEndDate();

  return {
    start: getWeekRange(start, firstDayOfWeek.value).start,
    end: getWeekRange(end, firstDayOfWeek.value).end,
  };
});

// Once a range is fully picked, show the whole weeks in the picker too. A half-picked range (one date)
// is left alone, so the picker can still take the second click.
watch(weekRange, ({ start, end }) => {
  const [first, last] = state.value.range;
  if (state.value.range.length === 2 && !(first && last && isSameDay(first, start) && isSameDay(last, end))) {
    state.value.range = [start, end];
  }
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
    // week entries aren't planned for a specific day
    if (meal.endDate) return false;

    const mealDate = parseISO(meal.date);
    return isSameDay(mealDate, date);
  });
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

/**
 * The visible days grouped by week, each with that week's entries, so meals can be planned for any visible week.
 * Week entries are grouped by their own dates rather than the current weeks, so they still show up (as a week
 * without days) if the household's first day of the week has changed since they were planned.
 */
const mealsByWeek = computed(() => {
  const weeks = new Map<string, { week: MealsByDate; days: MealsByDate[] }>();
  const getWeek = (start: Date, end: Date) => {
    const key = format(start, "yyyy-MM-dd");
    if (!weeks.has(key)) {
      weeks.set(key, { week: { date: start, endDate: end, meals: [] }, days: [] });
    }
    return weeks.get(key)!;
  };

  for (const day of mealsByDate.value) {
    const { start, end } = getWeekRange(day.date, firstDayOfWeek.value);
    getWeek(start, end).days.push(day);
  }

  for (const meal of mealplans.value ?? []) {
    if (meal.endDate) {
      getWeek(parseISO(meal.date), parseISO(meal.endDate)).week.meals.push(meal);
    }
  }

  return [...weeks.values()].sort((a, b) => a.week.date.getTime() - b.week.date.getTime());
});

/** Each week followed by its days, the order the planner pages lay them out in */
const plans = computed(() => mealsByWeek.value.flatMap(({ week, days }) => [week, ...days]));

const allMeals = computed(() => plans.value.flatMap(({ meals }) => meals));

const hasRecipes = computed(() => {
  return allMeals.value.some(meal => meal.recipe);
});

const weekRecipesWithScales = computed(() => {
  return getScaledRecipes(allMeals.value);
});
</script>
