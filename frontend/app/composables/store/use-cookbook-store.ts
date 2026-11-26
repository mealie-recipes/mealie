import type { Composer } from "vue-i18n";
import { useReadOnlyStore, useStore } from "../partials/use-store-factory";
import type { CookBookOut, CookBookUpdate } from "~/lib/api/types/cookbook";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

const cookbooks: Ref<CookBookOut[]> = ref([]);
const loading = ref(false);
const initialized = ref(false);
const publicLoading = ref(false);
const publicInitialized = ref(false);

export function resetCookbookStore() {
  cookbooks.value = [];
  loading.value = false;
  initialized.value = false;
  publicLoading.value = false;
  publicInitialized.value = false;
}

export const useCookbookStore = function (i18n?: Composer) {
  const api = useUserApi(i18n);
  const store = useStore<CookBookOut>("cookbook", cookbooks, loading, initialized, api.cookbooks);

  const updateAll = async function (updateData: CookBookUpdate[]) {
    loading.value = true;
    updateData.forEach((cookbook, index) => {
      cookbook.position = index;
    });
    const { data } = await api.cookbooks.updateAll(updateData);
    loading.value = false;
    return data;
  };
  return { ...store, updateAll };
};

export const usePublicCookbookStore = function (groupSlug: string, i18n?: Composer) {
  const api = usePublicExploreApi(groupSlug, i18n).explore;
  return useReadOnlyStore<CookBookOut>("cookbook", cookbooks, publicLoading, publicInitialized, api.cookbooks);
};
