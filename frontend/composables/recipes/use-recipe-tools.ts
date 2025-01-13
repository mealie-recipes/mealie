import { reactive, ref, useAsync } from "@nuxtjs/composition-api";
import { useAsyncKey } from "../use-utils";
import { useUserApi } from "~/composables/api";
import { VForm } from "~/types/vuetify";
import { RecipeTool } from "~/lib/api/types/recipe";

export const useTools = function (eager = true) {
  const workingToolData = reactive<RecipeTool>({
    id: "",
    name: "",
    slug: "",
  });

  const api = useUserApi();
  const loading = ref(false);
  const validForm = ref(false);

  const actions = {
    getAll() {
      loading.value = true;
      const units = useAsync(async () => {
        const { data } = await api.tools.getAll();

        if (data) {
          return data.items;
        } else {
          return null;
        }
      }, useAsyncKey());

      loading.value = false;
      return units;
    },

    async refreshAll() {
      loading.value = true;
      const { data } = await api.tools.getAll();

      if (data) {
        tools.value = data.items;
      }

      loading.value = false;
    },

    async createOne(domForm: VForm | null = null) {
      if (domForm && !domForm.validate()) {
        validForm.value = false;
      }

      loading.value = true;

      const { data } = await api.tools.createOne(workingToolData);

      if (data) {
        tools.value?.push(data);
      }

      domForm?.reset();
      this.reset();
    },

    async updateOne() {
      loading.value = true;
      const { data } = await api.tools.updateOne(workingToolData.id, workingToolData);
      if (data) {
        tools.value?.push(data);
      }
      this.reset();
    },

    async deleteOne(id: number) {
      loading.value = true;
      await api.tools.deleteOne(id);
      this.reset();
    },

    reset() {
      workingToolData.name = "";
      workingToolData.id = "";
      loading.value = false;
      validForm.value = true;
    },
  };

  const tools = (() => {
    if (eager) {
      return actions.getAll();
    } else {
      return ref([]);
    }
  })();

  return {
    tools,
    actions,
    workingToolData,
    loading,
  };
};
