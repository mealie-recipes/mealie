import { ref, Ref } from "@nuxtjs/composition-api";
import { useData, useReadOnlyStore, useStore } from "../partials/use-store-factory";
import { IngredientFood } from "~/lib/api/types/recipe";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

const store: Ref<IngredientFood[]> = ref([]);
const loading = ref(false);
const publicLoading = ref(false);

export const useFoodData = function () {
  return useData<IngredientFood>({
    id: "",
    name: "",
    description: "",
    labelId: undefined,
  });
}

export const useFoodStore = function () {
  const api = useUserApi();
  return useStore<IngredientFood>(store, loading, api.foods);
}

export const usePublicFoodStore = function (groupSlug: string) {
  const api = usePublicExploreApi(groupSlug).explore;
  return useReadOnlyStore<IngredientFood>(store, publicLoading, api.foods);
}
