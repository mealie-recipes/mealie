import { useAsync, ref } from "@nuxtjs/composition-api";
import { addDays, subDays, format } from "date-fns";
import { useAsyncKey } from "./use-utils";
import { useApiSingleton } from "~/composables/use-api";
import { CreateMealPlan, UpdateMealPlan } from "~/api/class-interfaces/group-mealplan";

export const useMealplans = function () {
  const api = useApiSingleton();
  const loading = ref(false);
  const validForm = ref(true);

  const actions = {
    getAll() {
      loading.value = true;
      const units = useAsync(async () => {
        const query = {
          start: format(subDays(new Date(), 30), "yyyy-MM-dd"),
          limit: format(addDays(new Date(), 30), "yyyy-MM-dd"),
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
        start: format(subDays(new Date(), 30), "yyyy-MM-dd"),
        limit: format(addDays(new Date(), 30), "yyyy-MM-dd"),
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
  };

  const mealplans = actions.getAll();

  return { mealplans, actions, validForm };
};
