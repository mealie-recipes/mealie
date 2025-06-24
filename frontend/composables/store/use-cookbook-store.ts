import { useReadOnlyStore, useStore } from "../partials/use-store-factory";
import type { RecipeCookBook } from "~/lib/api/types/cookbook";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

const store: Ref<RecipeCookBook[]> = ref([]);
const loading = ref(false);
const publicLoading = ref(false);

export const useCookbookStore = function () {
  const api = useUserApi();
  return useStore<RecipeCookBook>(store, loading, api.cookbooks);
};

export const usePublicCookbookStore = function (groupSlug: string) {
  const api = usePublicExploreApi(groupSlug).explore;
  return useReadOnlyStore<RecipeCookBook>(store, publicLoading, api.cookbooks);
};
