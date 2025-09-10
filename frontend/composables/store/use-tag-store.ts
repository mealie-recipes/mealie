import type { Composer } from "vue-i18n";
import { useData, useReadOnlyStore, useStore } from "../partials/use-store-factory";
import type { RecipeTag } from "~/lib/api/types/recipe";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

const store: Ref<RecipeTag[]> = ref([]);
const loading = ref(false);
const publicLoading = ref(false);

export const useTagData = function () {
  return useData<RecipeTag>({
    id: "",
    name: "",
    slug: "",
  });
};

export const useTagStore = function (i18n?: Composer) {
  const api = useUserApi(i18n);
  return useStore<RecipeTag>(store, loading, api.tags);
};

export const usePublicTagStore = function (groupSlug: string, i18n?: Composer) {
  const api = usePublicExploreApi(groupSlug, i18n).explore;
  return useReadOnlyStore<RecipeTag>(store, publicLoading, api.tags);
};
