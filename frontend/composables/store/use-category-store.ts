import { reactive, ref, Ref } from "@nuxtjs/composition-api";
import { usePublicStoreActions, useStoreActions } from "../partials/use-actions-factory";
import { usePublicExploreApi } from "../api/api-client";
import { useUserApi } from "~/composables/api";
import { RecipeCategory } from "~/lib/api/types/recipe";

const categoryStore: Ref<RecipeCategory[]> = ref([]);
const publicStoreLoading = ref(false);
const storeLoading = ref(false);

export function useCategoryData() {
  const data = reactive({
    id: "",
    name: "",
    slug: undefined,
  });

  function reset() {
    data.id = "";
    data.name = "";
    data.slug = undefined;
  }

  return {
    data,
    reset,
  };
}

export function usePublicCategoryStore(groupSlug: string) {
  const api = usePublicExploreApi(groupSlug).explore;
  const loading = publicStoreLoading;

  const actions = {
    ...usePublicStoreActions<RecipeCategory>(api.categories, categoryStore, loading),
    flushStore() {
      categoryStore.value = [];
    },
  };

  if (!loading.value && (!categoryStore.value || categoryStore.value?.length === 0)) {
    actions.getAll();
  }

  return {
    items: categoryStore,
    actions,
    loading,
  };
}

export function useCategoryStore() {
  // passing the group slug switches to using the public API
  const api = useUserApi();
  const loading = storeLoading;

  const actions = {
    ...useStoreActions<RecipeCategory>(api.categories, categoryStore, loading),
    flushStore() {
      categoryStore.value = [];
    },
  };

  if (!loading.value && (!categoryStore.value || categoryStore.value?.length === 0)) {
    actions.getAll();
  }

  return {
    items: categoryStore,
    actions,
    loading,
  };
}
