import { useAsync, ref, reactive, Ref } from "@nuxtjs/composition-api";
import { useAsyncKey } from "./use-utils";
import { useApiSingleton } from "~/composables/use-api";
import { ShoppingList } from "~/api/class-interfaces/shoppingLists";

let shoppingListStore: Ref<ShoppingList[] | null> | null = null;

export const useShoppingList = function () {
  function getOne(id: string | number) {
    const api = useApiSingleton();

    const units = useAsync(async () => {
      const { data } = await api.shoppingLists.getOne(id);

      return data;
    }, useAsyncKey());

    return units;
  }

  return { getOne };
};

export const useShoppingLists = function () {
  const api = useApiSingleton();
  const loading = ref(false);
  const deleteTargetId = ref(0);
  const validForm = ref(true);

  //  @ts-ignore
  const workingShoppingListData: ShoppingList = reactive({
    id: 0,
    name: "",
    position: 1,
    categories: [],
  });

  const actions = {
    getAll() {
      loading.value = true;
      const units = useAsync(async () => {
        const { data } = await api.shoppingLists.getAll();

        return data;
      }, useAsyncKey());

      loading.value = false;
      return units;
    },
    async refreshAll() {
      loading.value = true;
      const { data } = await api.shoppingLists.getAll();

      if (data && shoppingListStore) {
        shoppingListStore.value = data;
      }

      loading.value = false;
    },
    async createOne() {
      loading.value = true;
      const { data } = await api.shoppingLists.createOne({
        // @ts-ignore. I"m thinking this will always be defined.
        name: "Shopping List " + String(cookbookStore?.value?.length + 1 || 1),
      });
      if (data && shoppingListStore?.value) {
        shoppingListStore.value.push(data);
      } else {
        this.refreshAll();
      }

      this.resetWorking();
      loading.value = false;
    },
    async updateOne(updateData: ShoppingList) {
      if (!updateData.id) {
        return;
      }

      loading.value = true;
      const { data } = await api.shoppingLists.updateOne(updateData.id, updateData);
      if (data && shoppingListStore?.value) {
        this.refreshAll();
      }
      loading.value = false;
    },

    async updateOrder() {
      if (!shoppingListStore?.value) {
        return;
      }

      loading.value = true;

      shoppingListStore.value.forEach((element, index) => {
        element.position = index + 1;
      });

      const { data } = await api.shoppingLists.updateAll(shoppingListStore.value);

      if (data && shoppingListStore?.value) {
        this.refreshAll();
      }

      loading.value = true;
    },
    async deleteOne(id: string | number) {
      loading.value = true;
      const { data } = await api.shoppingLists.deleteOne(id);
      if (data && shoppingListStore?.value) {
        this.refreshAll();
      }
    },
    resetWorking() {
      workingShoppingListData.id = 0;
      workingShoppingListData.name = "";
      workingShoppingListData.position = 0;
      workingShoppingListData.categories = [];
    },
    setWorking(item: ShoppingList) {
      workingShoppingListData.id = item.id;
      workingShoppingListData.name = item.name;
      workingShoppingListData.position = item.position;
      workingShoppingListData.categories = item.categories;
    },
    flushStore() {
      shoppingListStore = null;
    },
  };

  if (!shoppingListStore) {
    shoppingListStore = actions.getAll();
  }

  return { shoppingLists: shoppingListStore, workingShoppingListData, deleteTargetId, actions, validForm };
};
