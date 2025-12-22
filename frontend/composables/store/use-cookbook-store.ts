import type { Composer } from "vue-i18n";
import { useReadOnlyStore, useStore } from "../partials/use-store-factory";
import type { ReadCookBook, UpdateCookBook } from "~/lib/api/types/cookbook";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

const cookbooks: Ref<ReadCookBook[]> = ref([]);
const loading = ref(false);
const publicLoading = ref(false);

export function resetCookbookStore() {
  cookbooks.value = [];
  loading.value = false;
  publicLoading.value = false;
}

export const useCookbookStore = function (i18n?: Composer) {
  const api = useUserApi(i18n);
  const store = useStore<ReadCookBook>("cookbook", cookbooks, loading, api.cookbooks);

  const updateAll = async function (updateData: UpdateCookBook[]) {
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
  return useReadOnlyStore<ReadCookBook>("cookbook", cookbooks, publicLoading, api.cookbooks);
};
