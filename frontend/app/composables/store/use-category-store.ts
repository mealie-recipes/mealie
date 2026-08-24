import type { Composer } from "vue-i18n";
import { useData, useReadOnlyStore, useStore } from "../partials/use-store-factory";
import type { RecipeCategory } from "~/lib/api/types/recipe";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

const store: Ref<RecipeCategory[]> = ref([]);
const loading = ref(false);
const initialized = ref(false);
const publicLoading = ref(false);
const publicInitialized = ref(false);

export function resetCategoryStore() {
  store.value = [];
  loading.value = false;
  initialized.value = false;
  publicLoading.value = false;
  publicInitialized.value = false;
}

export const useCategoryData = function () {
  return useData<RecipeCategory>({
    id: "",
    name: "",
    slug: "",
  });
};

export const useCategoryStore = function (i18n?: Composer) {
  const api = useUserApi(i18n);
  return useStore<RecipeCategory>("category", store, loading, initialized, api.categories);
};

export const usePublicCategoryStore = function (groupSlug: string, i18n?: Composer) {
  const api = usePublicExploreApi(groupSlug, i18n).explore;
  return useReadOnlyStore<RecipeCategory>("category", store, publicLoading, publicInitialized, api.categories);
};
