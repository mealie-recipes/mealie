import { useAsync, ref, Ref, watch } from "@nuxtjs/composition-api";
import { format } from "date-fns";
import { useAsyncKey } from "./use-utils";
import { useUserApi } from "~/composables/api";
import { CreatePlanEntry, PlanEntryType, UpdatePlanEntry } from "~/lib/api/types/meal-plan";

export const planTypeOptions = [
  { text: "Breakfast", value: "breakfast" },
  { text: "Lunch", value: "lunch" },
  { text: "Dinner", value: "dinner" },
  { text: "Side", value: "side" },
];

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
      const units = useAsync(async () => {
        const query = {
          start_date: format(range.value.start, "yyyy-MM-dd"),
          end_date: format(range.value.end, "yyyy-MM-dd"),
        };
        // @ts-ignore TODO Modify typing to allow for string start+limit for mealplans
        const { data } = await api.mealplans.getAll(1, -1, { start_date: query.start_date, end_date: query.end_date });

        if (data) {
          return data.items;
        } else {
          return null;
        }
      }, useAsyncKey());

      loading.value = false;
      return units;
    },
    async refreshAll(this: void) {
      loading.value = true;
      const query = {
        start_date: format(range.value.start, "yyyy-MM-dd"),
        end_date: format(range.value.end, "yyyy-MM-dd"),
      };
      // @ts-ignore TODO Modify typing to allow for string start+limit for mealplans
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
