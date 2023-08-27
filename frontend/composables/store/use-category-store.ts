import { reactive, ref, Ref } from "@nuxtjs/composition-api";
import { usePublicStoreActions, useStoreActions } from "../partials/use-actions-factory";
import { usePublicExploreApi } from "../api/api-client";
import { useUserApi } from "~/composables/api";
import { RecipeCategory } from "~/lib/api/types/admin";

const categoryStore: Ref<RecipeCategory[]> = ref([]);

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
  const loading = ref(false);

  const actions = {
    ...usePublicStoreActions<RecipeCategory>(api.categories, categoryStore, loading),
    flushStore() {
      categoryStore.value = [];
    },
  };

  if (!categoryStore.value || categoryStore.value?.length === 0) {
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
  const loading = ref(false);

  const actions = {
    ...useStoreActions<RecipeCategory>(api.categories, categoryStore, loading),
    flushStore() {
      categoryStore.value = [];
    },
  };

  if (!categoryStore.value || categoryStore.value?.length === 0) {
    actions.getAll();
  }

  return {
    items: categoryStore,
    actions,
    loading,
  };
}
