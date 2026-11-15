import type { Composer } from "vue-i18n";
import { useData, useStore } from "../partials/use-store-factory";
import type { IngredientUnitOut } from "~/lib/api/types/recipe";
import { useUserApi } from "~/composables/api";

const store: Ref<IngredientUnitOut[]> = ref([]);
const loading = ref(false);
const initialized = ref(false);

export function resetUnitStore() {
  store.value = [];
  loading.value = false;
  initialized.value = false;
}

export const useUnitData = function () {
  return useData<IngredientUnitOut>({
    id: "",
    name: "",
    pluralName: null,
    description: "",
    extras: {},
    fraction: true,
    abbreviation: "",
    pluralAbbreviation: "",
    useAbbreviation: false,
    aliases: [],
    standardQuantity: null,
    standardUnit: null,
    createdAt: null,
    updatedAt: null,
  });
};

export const useUnitStore = function (i18n?: Composer) {
  const api = useUserApi(i18n);
  return useStore<IngredientUnitOut>("unit", store, loading, initialized, api.units);
};
