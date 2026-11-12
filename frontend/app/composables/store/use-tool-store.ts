import type { Composer } from "vue-i18n";
import { useData, useReadOnlyStore, useStore } from "../partials/use-store-factory";
import type { ToolOut } from "~/lib/api/types/recipe";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

/** A tool with whether the current user's household owns it. */
export interface RecipeToolWithOnHand extends ToolOut {
  onHand: boolean;
}

const store: Ref<ToolOut[]> = ref([]);
const loading = ref(false);
const initialized = ref(false);
const publicLoading = ref(false);
const publicInitialized = ref(false);

export function resetToolStore() {
  store.value = [];
  loading.value = false;
  initialized.value = false;
  publicLoading.value = false;
  publicInitialized.value = false;
}

export const useToolData = function () {
  return useData<RecipeToolWithOnHand>({
    id: "",
    groupId: "",
    name: "",
    slug: "",
    recipeCount: 0,
    onHand: false,
    householdsWithTool: [],
  });
};

export const useToolStore = function (i18n?: Composer) {
  const api = useUserApi(i18n);
  return useStore<ToolOut>("tool", store, loading, initialized, api.tools);
};

export const usePublicToolStore = function (groupSlug: string, i18n?: Composer) {
  const api = usePublicExploreApi(groupSlug, i18n).explore;
  return useReadOnlyStore<ToolOut>("tool", store, publicLoading, publicInitialized, api.tools);
};
