import { ref, Ref } from "@nuxtjs/composition-api";
import { useData, useReadOnlyStore, useStore } from "../partials/use-store-factory";
import { RecipeCategory } from "~/lib/api/types/recipe";
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
  return useReadOnlyStore<RecipeCategory>(store, publicLoading, api.categories);
}
