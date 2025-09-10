import type { Composer } from "vue-i18n";
import { useData, useReadOnlyStore, useStore } from "../partials/use-store-factory";
import type { RecipeTool } from "~/lib/api/types/recipe";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

interface RecipeToolWithOnHand extends RecipeTool {
  onHand: boolean;
}

const store: Ref<RecipeTool[]> = ref([]);
const loading = ref(false);
const publicLoading = ref(false);

export const useToolData = function () {
  return useData<RecipeToolWithOnHand>({
    id: "",
    name: "",
    slug: "",
    onHand: false,
    householdsWithTool: [],
  });
};

export const useToolStore = function (i18n?: Composer) {
  const api = useUserApi(i18n);
  return useStore<RecipeTool>(store, loading, api.tools);
};

export const usePublicToolStore = function (groupSlug: string, i18n?: Composer) {
  const api = usePublicExploreApi(groupSlug, i18n).explore;
  return useReadOnlyStore<RecipeTool>(store, publicLoading, api.tools);
};
