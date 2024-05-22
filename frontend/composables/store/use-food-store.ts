import { ref, reactive, Ref } from "@nuxtjs/composition-api";
import { usePublicStoreActions, useStoreActions } from "../partials/use-actions-factory";
import { usePublicExploreApi } from "../api/api-client";
import { useUserApi } from "~/composables/api";
import { IngredientFood } from "~/lib/api/types/recipe";

let foodStore: Ref<IngredientFood[] | null> = ref([]);
const publicStoreLoading = ref(false);
const storeLoading = ref(false);

/**
 * useFoodData returns a template reactive object
 * for managing the creation of foods. It also provides a
 * function to reset the data back to the initial state.
 */
export const useFoodData = function () {
  const data: IngredientFood = reactive({
    id: "",
    name: "",
    description: "",
    labelId: undefined,
  });

  function reset() {
    data.id = "";
    data.name = "";
    data.description = "";
    data.labelId = undefined;
  }

  return {
    data,
    reset,
  };
};

export const usePublicFoodStore = function (groupSlug: string) {
  const api = usePublicExploreApi(groupSlug).explore;
  const loading = publicStoreLoading;

  const actions = {
    ...usePublicStoreActions(api.foods, foodStore, loading),
    flushStore() {
      foodStore = ref([]);
    },
  };

  if (!loading.value && (!foodStore.value || foodStore.value.length === 0)) {
    foodStore = actions.getAll();
  }

  return { foods: foodStore, actions };
};

export const useFoodStore = function () {
  const api = useUserApi();
  const loading = storeLoading;

  const actions = {
    ...useStoreActions(api.foods, foodStore, loading),
    flushStore() {
      foodStore.value = [];
    },
  };

  if (!loading.value && (!foodStore.value || foodStore.value.length === 0)) {
    foodStore = actions.getAll();
  }

  return { foods: foodStore, actions };
};
