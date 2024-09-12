import { ref, Ref } from "@nuxtjs/composition-api";
import { RecipeTool } from "~/lib/api/types/recipe";
import { useData, usePublicStore, useStore } from "../partials/use-store-factory";
import { usePublicExploreApi, useUserApi } from "~/composables/api";

const store: Ref<RecipeTool[]> = ref([]);
const loading = ref(false);
const publicLoading = ref(false);

export const useToolData = function () {
  return useData<RecipeTool>({
    id: "",
    name: "",
    slug: "",
    onHand: false,
  });
}

export const useToolStore = function () {
  const api = useUserApi();
  return useStore<RecipeTool>(store, loading, api.tools);
}

export const usePublicToolStore = function (groupSlug: string) {
  const api = usePublicExploreApi(groupSlug).explore;
  return usePublicStore<RecipeTool>(store, publicLoading, api.tools);
}
