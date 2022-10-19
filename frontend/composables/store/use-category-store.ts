import { reactive, ref, Ref } from "@nuxtjs/composition-api";
import { useStoreActions } from "../partials/use-actions-factory";
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

export function useCategoryStore() {
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
