import { reactive, ref, Ref } from "@nuxtjs/composition-api";
import { useStoreActions } from "../partials/use-actions-factory";
import { useUserApi } from "~/composables/api";
import { RecipeTag } from "~/lib/api/types/admin";

const items: Ref<RecipeTag[]> = ref([]);

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
