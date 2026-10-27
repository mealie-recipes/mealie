import { addDays, format, startOfWeek } from "date-fns";
import type { Day } from "date-fns";
import { useHouseholdSelf } from "./use-households";
import { useAsyncKey } from "./use-utils";
import { useUserApi } from "~/composables/api";
import type { CreatePlanEntry, PlanEntryType, ReadPlanEntry, RecipeSummary, UpdatePlanEntry } from "~/lib/api/types/meal-plan";

type PlanOption = {
  text: string;
  value: PlanEntryType;
};
export function usePlanTypeOptions() {
  const i18n = useI18n();

  return [
    { text: i18n.t("meal-plan.breakfast"), value: "breakfast" },
    { text: i18n.t("meal-plan.lunch"), value: "lunch" },
    { text: i18n.t("meal-plan.dinner"), value: "dinner" },
    { text: i18n.t("meal-plan.side"), value: "side" },
    { text: i18n.t("meal-plan.snack"), value: "snack" },
    { text: i18n.t("meal-plan.drink"), value: "drink" },
    { text: i18n.t("meal-plan.dessert"), value: "dessert" },
  ] as PlanOption[];
}

export function getEntryTypeText(value: PlanEntryType) {
  const i18n = useI18n();
  return i18n.t("meal-plan." + value);
}
export interface DateRange {
  start: Date;
  end: Date;
}

/**
 * The week containing `date`, used as the `date` and `endDate` of a meal plan entry planned for that week.
 * `firstDayOfWeek` is the household preference (0 is Sunday).
 */
export function getWeekRange(date: Date, firstDayOfWeek: number): DateRange {
  const start = startOfWeek(date, { weekStartsOn: firstDayOfWeek as Day });
  return { start, end: addDays(start, 6) };
}

/**
 * Date state for a meal plan entry form: either the selected day, or the week containing it.
 */
export function useMealPlanEntryDates() {
  const { household } = useHouseholdSelf();

  const selectedDate = ref(new Date());
  const isWeekEntry = ref(false);

  const weekRange = computed(() => getWeekRange(selectedDate.value, household.value?.preferences?.firstDayOfWeek || 0));

  const entryDates = computed(() => isWeekEntry.value
    ? { date: weekRange.value.start, endDate: weekRange.value.end }
    : { date: selectedDate.value, endDate: null },
  );

  /** `date` and `endDate` formatted for the API */
  const entryDatesPayload = computed(() => ({
    date: format(entryDates.value.date, "yyyy-MM-dd"),
    endDate: entryDates.value.endDate ? format(entryDates.value.endDate, "yyyy-MM-dd") : null,
  }));

  /**
   * `v-model` for `MealPlanDatePicker`, used with `pickerMultiple`. For a week entry it's the whole week, so the
   * picker highlights it as a range. Clicking a day in range mode replaces the range with just that day, which
   * selects the week containing it.
   */
  const pickerModel = computed<Date | [Date, Date]>({
    get: () => isWeekEntry.value ? [weekRange.value.start, weekRange.value.end] : selectedDate.value,
    set: (value) => {
      const date = Array.isArray(value) ? value[0] : value;
      if (date) {
        selectedDate.value = date;
      }
    },
  });
  const pickerMultiple = computed(() => isWeekEntry.value ? "range" as const : false);

  return { selectedDate, isWeekEntry, weekRange, entryDates, entryDatesPayload, pickerModel, pickerMultiple };
}
export type DaySection = {
  title: string;
  meals: ReadPlanEntry[];
};

export type ScaledRecipe = RecipeSummary & { scale: number };

export type Days = {
  date: Date;
  /** Set for a week, whose meals aren't planned for a specific day */
  endDate?: Date | null;
  sections: DaySection[];
  recipes: ScaledRecipe[];
};

/**
 * The recipes of the given meal plan entries, each carrying the scale set on its entry.
 * Entries without a recipe (notes) are skipped.
 */
export function getScaledRecipes(meals: ReadPlanEntry[]): ScaledRecipe[] {
  return meals.flatMap(meal => meal.recipe ? [{ ...meal.recipe, scale: meal.recipeScale ?? 1 }] : []);
}

export type MealsByDate = {
  date: Date;
  /** Set for a week, whose meals aren't planned for a specific day */
  endDate?: Date | null;
  meals: ReadPlanEntry[];
};

export interface Meal {
  date: Date;
  title: string;
  text: string;
  recipeId?: string;
  entryType: PlanEntryType;
  existing: boolean;
  id: number;
  groupId: string;
  userId: string;
  note: boolean;
  householdId: string;
}

export const useMealplans = function (range: Ref<DateRange>) {
  const api = useUserApi();
  const loading = ref(false);

  const actions = {
    getAll() {
      loading.value = true;
      const { data: units } = useAsyncData(useAsyncKey(), async () => {
        const query = {
          start_date: format(range.value.start, "yyyy-MM-dd"),
          end_date: format(range.value.end, "yyyy-MM-dd"),
        };
        const { data } = await api.mealplans.getAll(1, -1, {
          start_date: query.start_date,
          end_date: query.end_date,
          include_week_entries: true,
        });

        if (data) {
          return data.items;
        }
        else {
          return null;
        }
      });

      loading.value = false;
      return units;
    },
    async refreshAll() {
      loading.value = true;
      const query = {
        start_date: format(range.value.start, "yyyy-MM-dd"),
        end_date: format(range.value.end, "yyyy-MM-dd"),
      };
      const { data } = await api.mealplans.getAll(1, -1, {
        start_date: query.start_date,
        end_date: query.end_date,
        include_week_entries: true,
      });

      if (data && data.items) {
        mealplans.value = data.items;
      }

      loading.value = false;
    },
    async createOne(payload: CreatePlanEntry) {
      loading.value = true;

      const { data } = await api.mealplans.createOne(payload);
      if (data) {
        this.refreshAll();
      }

      loading.value = false;
    },
    async updateOne(updateData: UpdatePlanEntry) {
      if (!updateData.id) {
        return;
      }

      loading.value = true;
      const { data } = await api.mealplans.updateOne(updateData.id, updateData);
      if (data) {
        this.refreshAll();
      }
      loading.value = false;
    },

    async deleteOne(id: string | number) {
      loading.value = true;
      const { data } = await api.mealplans.deleteOne(id);
      if (data) {
        this.refreshAll();
      }
      loading.value = false;
    },

    async setType(payload: UpdatePlanEntry, type: PlanEntryType) {
      payload.entryType = type;
      await this.updateOne(payload);
    },
  };

  const mealplans = actions.getAll();

  watch(range, actions.refreshAll);

  return { mealplans, actions, loading };
};
