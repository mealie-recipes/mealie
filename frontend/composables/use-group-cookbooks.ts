import { useAsync, ref, reactive, Ref } from "@nuxtjs/composition-api";
import { useAsyncKey } from "./use-utils";
import { useUserApi } from "~/composables/api";
import { CookBook } from "~/api/class-interfaces/group-cookbooks";

let cookbookStore: Ref<CookBook[] | null> | null = null;

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
  const deleteTargetId = ref(0);
  const validForm = ref(true);

  //  @ts-ignore
  const workingCookbookData: CookBook = reactive({
    id: 0,
    name: "",
    position: 1,
    categories: [],
  });

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
        // @ts-ignore. I"m thinking this will always be defined.
        name: "Cookbook " + String(cookbookStore?.value?.length + 1 || 1),
      });
      if (data && cookbookStore?.value) {
        cookbookStore.value.push(data);
      } else {
        this.refreshAll();
      }

      this.resetWorking();
      loading.value = false;
    },
    async updateOne(updateData: CookBook) {
      if (!updateData.id) {
        return;
      }

      loading.value = true;
      const { data } = await api.cookbooks.updateOne(updateData.id, updateData);
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
    resetWorking() {
      workingCookbookData.id = 0;
      workingCookbookData.name = "";
      workingCookbookData.position = 0;
      workingCookbookData.categories = [];
    },
    setWorking(item: CookBook) {
      workingCookbookData.id = item.id;
      workingCookbookData.name = item.name;
      workingCookbookData.position = item.position;
      workingCookbookData.categories = item.categories;
    },
    flushStore() {
      cookbookStore = null;
    },
  };

  if (!cookbookStore) {
    cookbookStore = actions.getAll();
  }

  return { cookbooks: cookbookStore, workingCookbookData, deleteTargetId, actions, validForm };
};
