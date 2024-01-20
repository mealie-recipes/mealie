import { reactive, ref, Ref } from "@nuxtjs/composition-api";
import { usePublicStoreActions, useStoreActions } from "../partials/use-actions-factory";
import { usePublicExploreApi } from "../api/api-client";
import { useUserApi } from "~/composables/api";
import { RecipeTag } from "~/lib/api/types/admin";

const items: Ref<RecipeTag[]> = ref([]);
const publicTagStore: { [slug: string]: Ref<RecipeTag[]> } = {};

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
  const loading = ref(false);

  const actions = {
    ...usePublicStoreActions<RecipeTag>(api.tags, publicTagStore[groupSlug], loading),
    flushStore() {
      publicTagStore[groupSlug].value = [];
    },
  };

  if (!publicTagStore[groupSlug]?.value || publicTagStore[groupSlug]?.value?.length === 0) {
    actions.getAll();
  }

  return {
    items: publicTagStore[groupSlug],
    actions,
    loading,
  };
}

export function useTagStore() {
  const api = useUserApi();
  const loading = ref(false);

  const actions = {
    ...useStoreActions<RecipeTag>(api.tags, items, loading),
    flushStore() {
      items.value = [];
    },
  };

  if (!items.value || items.value?.length === 0) {
    actions.getAll();
  }

  return {
    items,
    actions,
    loading,
  };
}
