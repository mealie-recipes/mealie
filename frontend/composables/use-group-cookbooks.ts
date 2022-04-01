import { useAsync, ref, Ref } from "@nuxtjs/composition-api";
import { useAsyncKey } from "./use-utils";
import { useUserApi } from "~/composables/api";
import { ReadCookBook, RecipeCookBook, UpdateCookBook } from "~/types/api-types/cookbook";

let cookbookStore: Ref<ReadCookBook[] | null> | null = null;

export const useCookbook = function () {
  function getOne(id: string | number) {
    const api = useUserApi();

    const units = useAsync(async () => {
      const { data } = await api.cookbooks.getOne(id);

      return data;
    }, useAsyncKey());

    return units;
  }

  return { getOne };
};

export const useCookbooks = function () {
  const api = useUserApi();
  const loading = ref(false);

  const actions = {
    getAll() {
      loading.value = true;
      const units = useAsync(async () => {
        const { data } = await api.cookbooks.getAll();

        return data;
      }, useAsyncKey());

      loading.value = false;
      return units;
    },
    async refreshAll() {
      loading.value = true;
      const { data } = await api.cookbooks.getAll();

      if (data && cookbookStore) {
        cookbookStore.value = data;
      }

      loading.value = false;
    },
    async createOne() {
      loading.value = true;
      const { data } = await api.cookbooks.createOne({
        name: "Cookbook " + String((cookbookStore?.value?.length ?? 0) + 1),
      });
      if (data && cookbookStore?.value) {
        cookbookStore.value.push(data);
      } else {
        this.refreshAll();
      }

      loading.value = false;
    },
    async updateOne(updateData: UpdateCookBook) {
      if (!updateData.id) {
        return;
      }

      loading.value = true;
      const { data } = await api.cookbooks.updateOne(updateData.id, updateData as RecipeCookBook);
      if (data && cookbookStore?.value) {
        this.refreshAll();
      }
      loading.value = false;
    },

    async updateOrder() {
      if (!cookbookStore?.value) {
        return;
      }

      loading.value = true;

      cookbookStore.value.forEach((element, index) => {
        element.position = index + 1;
      });

      const { data } = await api.cookbooks.updateAll(cookbookStore.value);

      if (data && cookbookStore?.value) {
        this.refreshAll();
      }

      loading.value = true;
    },
    async deleteOne(id: string | number) {
      loading.value = true;
      const { data } = await api.cookbooks.deleteOne(id);
      if (data && cookbookStore?.value) {
        this.refreshAll();
      }
    },
    flushStore() {
      cookbookStore = null;
    },
  };

  if (!cookbookStore) {
    cookbookStore = actions.getAll();
  }

  return { cookbooks: cookbookStore, actions };
};
