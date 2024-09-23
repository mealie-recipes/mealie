import { ref, Ref } from "@nuxtjs/composition-api";
import { useData, useReadOnlyStore, useStore } from "../partials/use-store-factory";
import { RecipeTool } from "~/lib/api/types/recipe";
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
  return useReadOnlyStore<RecipeTool>(store, publicLoading, api.tools);
}
