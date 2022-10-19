import { ref, reactive, Ref } from "@nuxtjs/composition-api";
import { useStoreActions } from "../partials/use-actions-factory";
import { useUserApi } from "~/composables/api";
import { IngredientUnit } from "~/lib/api/types/recipe";

let unitStore: Ref<IngredientUnit[] | null> | null = null;

/**
 * useUnitData returns a template reactive object
 * for managing the creation of units. It also provides a
 * function to reset the data back to the initial state.
 */
export const useUnitData = function () {
  const data: IngredientUnit = reactive({
    id: "",
    name: "",
    fraction: true,
    abbreviation: "",
    description: "",
  });

  function reset() {
    data.id = "";
    data.name = "";
    data.fraction = true;
    data.abbreviation = "";
    data.description = "";
  }

  return {
    data,
    reset,
  };
};

export const useUnitStore = function () {
  const api = useUserApi();
  const loading = ref(false);

  const actions = {
    ...useStoreActions<IngredientUnit>(api.units, unitStore, loading),
    flushStore() {
      unitStore = null;
    },
  };

  if (!unitStore) {
    unitStore = actions.getAll();
  }

  return { units: unitStore, actions };
};
