import { useAsync, ref, Ref, watch } from "@nuxtjs/composition-api";
import { format } from "date-fns";
import { useAsyncKey } from "./use-utils";
import { useUserApi } from "~/composables/api";
import { CreateMealPlan, UpdateMealPlan } from "~/api/class-interfaces/group-mealplan";

export type MealType = "breakfast" | "lunch" | "dinner" | "snack";

export const planTypeOptions = [
  { text: "Breakfast", value: "breakfast" },
  { text: "Lunch", value: "lunch" },
  { text: "Dinner", value: "dinner" },
  { text: "Snack", value: "snack" },
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
          start: format(range.value.start, "yyyy-MM-dd"),
          limit: format(range.value.end, "yyyy-MM-dd"),
        };
        // @ts-ignore
        const { data } = await api.mealplans.getAll(query.start, query.limit);

        return data;
      }, useAsyncKey());

      loading.value = false;
      return units;
    },
    async refreshAll() {
      loading.value = true;
      const query = {
        start: format(range.value.start, "yyyy-MM-dd"),
        limit: format(range.value.end, "yyyy-MM-dd"),
      };
      // @ts-ignore
      const { data } = await api.mealplans.getAll(query.start, query.limit);

      if (data) {
        mealplans.value = data;
      }

      loading.value = false;
    },
    async createOne(payload: CreateMealPlan) {
      loading.value = true;

      const { data } = await api.mealplans.createOne(payload);
      if (data) {
        this.refreshAll();
      }

      loading.value = false;
    },
    async updateOne(updateData: UpdateMealPlan) {
      if (!updateData.id) {
        return;
      }

      loading.value = true;
      // @ts-ignore
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

    async setType(payload: UpdateMealPlan, typ: MealType) {
      payload.entryType = typ;
      await this.updateOne(payload);
    },
  };

  const mealplans = actions.getAll();

  watch(range, actions.refreshAll);

  return { mealplans, actions, validForm, loading };
};
