import { ref, Ref } from "@nuxtjs/composition-api";
import { RecipeTag } from "~/lib/api/types/recipe";
import { useData, usePublicStore, useStore } from "../partials/use-store-factory";
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
  return usePublicStore<RecipeTag>(store, publicLoading, api.tags);
}
