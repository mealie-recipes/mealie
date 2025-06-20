import { format } from "date-fns";
import { useAsyncKey } from "./use-utils";
import { useUserApi } from "~/composables/api";
import type { CreatePlanEntry, PlanEntryType, UpdatePlanEntry } from "~/lib/api/types/meal-plan";

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

export const useMealplans = function (range: Ref<DateRange>) {
  const api = useUserApi();
  const loading = ref(false);
  const validForm = ref(true);

  const actions = {
    getAll() {
      loading.value = true;
      const { data: units } = useAsyncData(useAsyncKey(), async () => {
        const query = {
          start_date: format(range.value.start, "yyyy-MM-dd"),
          end_date: format(range.value.end, "yyyy-MM-dd"),
        };
        const { data } = await api.mealplans.getAll(1, -1, { start_date: query.start_date, end_date: query.end_date });

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
      const { data } = await api.mealplans.getAll(1, -1, { start_date: query.start_date, end_date: query.end_date });

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
    },

    async setType(payload: UpdatePlanEntry, type: PlanEntryType) {
      payload.entryType = type;
      await this.updateOne(payload);
    },
  };

  const mealplans = actions.getAll();

  watch(range, actions.refreshAll);

  return { mealplans, actions, validForm, loading };
};
