import { useReadOnlyStore } from "../partials/use-store-factory";
import { usePublicExploreApi, useUserApi } from "~/composables/api";
import type { RecipeCookBook } from "~/lib/api/types/cookbook";

const store: Ref<RecipeCookBook[]> = ref([]);
const loading = ref(false);
const publicLoading = ref(false);

export const useCookbookStore = function () {
  const api = useUserApi();
  return useReadOnlyStore<RecipeCookBook>(store, loading, api.cookbooks);
};

export const usePublicCookbookStore = function (groupSlug: string) {
  const api = usePublicExploreApi(groupSlug).explore;
  return useReadOnlyStore<RecipeCookBook>(store, publicLoading, api.cookbooks);
};
