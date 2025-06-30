import { useReadOnlyStore, useStore } from "../partials/use-store-factory";
import type { RecipeCookBook } from "~/lib/api/types/cookbook";
import { usePublicExploreApi, useUserApi } from "~/composables/api";
import type { Composer } from "vue-i18n";

const store: Ref<RecipeCookBook[]> = ref([]);
const loading = ref(false);
const publicLoading = ref(false);

export const useCookbookStore = function () {
  const api = useUserApi();
  return useStore<RecipeCookBook>(store, loading, api.cookbooks);
};

export const usePublicCookbookStore = function (groupSlug: string, i18n?: Composer) {
  const api = usePublicExploreApi(groupSlug, i18n).explore;
  return useReadOnlyStore<RecipeCookBook>(store, publicLoading, api.cookbooks);
};
