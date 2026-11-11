import type { Composer } from "vue-i18n";
import { useData, useReadOnlyStore, useStore } from "../partials/use-store-factory";
import type { TagOut } from "~/lib/api/types/recipe";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

const store: Ref<TagOut[]> = ref([]);
const loading = ref(false);
const initialized = ref(false);
const publicLoading = ref(false);
const publicInitialized = ref(false);

export function resetTagStore() {
  store.value = [];
  loading.value = false;
  initialized.value = false;
  publicLoading.value = false;
  publicInitialized.value = false;
}

export const useTagData = function () {
  return useData<TagOut>({
    id: "",
    groupId: "",
    name: "",
    slug: "",
    recipeCount: 0,
  });
};

export const useTagStore = function (i18n?: Composer) {
  const api = useUserApi(i18n);
  return useStore<TagOut>("tag", store, loading, initialized, api.tags);
};

export const usePublicTagStore = function (groupSlug: string, i18n?: Composer) {
  const api = usePublicExploreApi(groupSlug, i18n).explore;
  return useReadOnlyStore<TagOut>("tag", store, publicLoading, publicInitialized, api.tags);
};
