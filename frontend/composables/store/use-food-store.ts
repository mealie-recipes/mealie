import { ref, reactive, Ref } from "@nuxtjs/composition-api";
import { useStoreActions } from "../partials/use-actions-factory";
import { useUserApi } from "~/composables/api";
import { IngredientFood } from "~/lib/api/types/recipe";

let foodStore: Ref<IngredientFood[] | null> | null = null;

/**
 * useFoodData returns a template reactive object
 * for managing the creation of units. It also provides a
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

export const useFoodStore = function () {
  const api = useUserApi();
  const loading = ref(false);

  const actions = {
    ...useStoreActions(api.foods, foodStore, loading),
    flushStore() {
      foodStore = null;
    },
  };

  if (!foodStore) {
    foodStore = actions.getAll();
  }

  return { foods: foodStore, actions };
};
