import { ref, Ref } from "@nuxtjs/composition-api";
import { RecipeCategory } from "~/lib/api/types/recipe";
import { useData, usePublicStore, useStore } from "../partials/use-store-factory";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

const store: Ref<RecipeCategory[]> = ref([]);
const loading = ref(false);
const publicLoading = ref(false);

export const useCategoryData = function () {
  return useData<RecipeCategory>({
    id: "",
    name: "",
    slug: "",
  });
}

export const useCategoryStore = function () {
  const api = useUserApi();
  return useStore<RecipeCategory>(store, loading, api.categories);
}

export const usePublicCategoryStore = function (groupSlug: string) {
  const api = usePublicExploreApi(groupSlug).explore;
  return usePublicStore<RecipeCategory>(store, publicLoading, api.categories);
}
