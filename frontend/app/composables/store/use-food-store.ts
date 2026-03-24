import type { Composer } from "vue-i18n";
import { useData, useReadOnlyStore, useStore } from "../partials/use-store-factory";
import type { IngredientFood } from "~/lib/api/types/recipe";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

const store: Ref<IngredientFood[]> = ref([]);
const loading = ref(false);
const publicLoading = ref(false);

export function resetFoodStore() {
  store.value = [];
  loading.value = false;
  publicLoading.value = false;
}

export const useFoodData = function () {
  return useData<IngredientFood>({
    id: "",
    name: "",
    description: "",
    labelId: undefined,
  });
};

export const useFoodStore = function (i18n?: Composer) {
  const api = useUserApi(i18n);
  return useStore<IngredientFood>("food", store, loading, api.foods);
};

export const usePublicFoodStore = function (groupSlug: string, i18n?: Composer) {
  const api = usePublicExploreApi(groupSlug, i18n).explore;
  return useReadOnlyStore<IngredientFood>("food", store, publicLoading, api.foods);
};
