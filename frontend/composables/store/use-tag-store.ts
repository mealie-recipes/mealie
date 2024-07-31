import { reactive, ref, Ref } from "@nuxtjs/composition-api";
import { usePublicStoreActions, useStoreActions } from "../partials/use-actions-factory";
import { usePublicExploreApi } from "../api/api-client";
import { useUserApi } from "~/composables/api";
import { RecipeTag } from "~/lib/api/types/recipe";

const items: Ref<RecipeTag[]> = ref([]);
const publicStoreLoading = ref(false);
const storeLoading = ref(false);

export function useTagData() {
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

export function usePublicTagStore(groupSlug: string) {
  const api = usePublicExploreApi(groupSlug).explore;
  const loading = publicStoreLoading;

  const actions = {
    ...usePublicStoreActions<RecipeTag>(api.tags, items, loading),
    flushStore() {
      items.value = [];
    },
  };

  if (!loading.value && (!items.value || items.value?.length === 0)) {
    actions.getAll();
  }

  return {
    items,
    actions,
    loading,
  };
}

export function useTagStore() {
  const api = useUserApi();
  const loading = storeLoading;

  const actions = {
    ...useStoreActions<RecipeTag>(api.tags, items, loading),
    flushStore() {
      items.value = [];
    },
  };

  if (!loading.value && (!items.value || items.value?.length === 0)) {
    actions.getAll();
  }

  return {
    items,
    actions,
    loading,
  };
}
