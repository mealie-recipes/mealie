import { ref, Ref } from "@nuxtjs/composition-api";
import { useData, useReadOnlyStore, useStore } from "../partials/use-store-factory";
import { RecipeTag } from "~/lib/api/types/recipe";
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
}

export const useTagStore = function () {
  const api = useUserApi();
  return useStore<RecipeTag>(store, loading, api.tags);
}

export const usePublicTagStore = function (groupSlug: string) {
  const api = usePublicExploreApi(groupSlug).explore;
  return useReadOnlyStore<RecipeTag>(store, publicLoading, api.tags);
}
