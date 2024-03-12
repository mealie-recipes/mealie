import { reactive, ref, Ref } from "@nuxtjs/composition-api";
import { usePublicExploreApi } from "../api/api-client";
import { usePublicStoreActions, useStoreActions } from "../partials/use-actions-factory";
import { useUserApi } from "~/composables/api";
import { RecipeTool } from "~/lib/api/types/recipe";

const toolStore: Ref<RecipeTool[]> = ref([]);
const publicStoreLoading = ref(false);
const storeLoading = ref(false);

export function useToolData() {
  const data = reactive({
    id: "",
    name: "",
    slug: undefined,
    onHand: false,
  });

  function reset() {
    data.id = "";
    data.name = "";
    data.slug = undefined;
    data.onHand = false;
  }

  return {
    data,
    reset,
  };
}

export function usePublicToolStore(groupSlug: string) {
  const api = usePublicExploreApi(groupSlug).explore;
  const loading = publicStoreLoading;

  const actions = {
    ...usePublicStoreActions<RecipeTool>(api.tools, toolStore, loading),
    flushStore() {
      toolStore.value = [];
    },
  };

  if (!loading.value && (!toolStore.value || toolStore.value?.length === 0)) {
    actions.getAll();
  }

  return {
    items: toolStore,
    actions,
    loading,
  };
}

export function useToolStore() {
  const api = useUserApi();
  const loading = storeLoading;

  const actions = {
    ...useStoreActions<RecipeTool>(api.tools, toolStore, loading),
    flushStore() {
      toolStore.value = [];
    },
  };

  if (!loading.value && (!toolStore.value || toolStore.value?.length === 0)) {
    actions.getAll();
  }

  return {
    items: toolStore,
    actions,
    loading,
  };
}
