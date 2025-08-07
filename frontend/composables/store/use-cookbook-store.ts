import type { Composer } from "vue-i18n";
import { useReadOnlyStore, useStore } from "../partials/use-store-factory";
import type { RecipeCookBook } from "~/lib/api/types/cookbook";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

const store: Ref<RecipeCookBook[]> = ref([]);
const loading = ref(false);
const publicLoading = ref(false);

export const useCookbookStore = function (i18n?: Composer) {
  const api = useUserApi(i18n);
  return useStore<RecipeCookBook>(store, loading, api.cookbooks);
};

export const usePublicCookbookStore = function (groupSlug: string, i18n?: Composer) {
  const api = usePublicExploreApi(groupSlug, i18n).explore;
  return useReadOnlyStore<RecipeCookBook>(store, publicLoading, api.cookbooks);
};
