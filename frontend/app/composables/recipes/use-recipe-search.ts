import { watchDebounced } from "@vueuse/core";
import type { UserApi } from "~/lib/api";
import type { ExploreApi } from "~/lib/api/public/explore";
import type { RecipeSummary } from "~/lib/api/types/recipe";

export interface UseRecipeSearchReturn {
  query: Ref<string>;
  mode: Ref<"all" | "any">;
  error: Ref<string>;
  loading: Ref<boolean>;
  data: Ref<RecipeSummary[]>;
  trigger(): Promise<void>;
}

/** Search recipes with debounce and discard responses for superseded queries. */
export function useRecipeSearch(api: UserApi | ExploreApi): UseRecipeSearchReturn {
  const query = ref("");
  const mode = ref<"all" | "any">("all");
  const error = ref("");
  const loading = ref(false);
  const recipes = ref<RecipeSummary[]>([]);
  let requestId = 0;

  async function searchRecipes() {
    const currentRequest = ++requestId;
    const term = query.value;
    const searchMode = mode.value;
    loading.value = true;
    error.value = "";
    try {
      const result = await api.recipes.search({
        search: term,
        searchMode,
        page: 1,
        orderBy: "name",
        orderDirection: "asc",
        perPage: 20,
        _searchSeed: Date.now().toString(),
      });
      if (currentRequest !== requestId || term !== query.value || searchMode !== mode.value) return;
      if (result.error) {
        error.value = [400, 422].includes(result.error.response?.status ?? 0)
          ? "search.invalid-query"
          : "search.request-failed";
        recipes.value = [];
      }
      else {
        recipes.value = result.data?.items ?? [];
      }
    }
    catch {
      if (currentRequest === requestId) {
        error.value = "search.request-failed";
        recipes.value = [];
      }
    }
    finally {
      if (currentRequest === requestId) loading.value = false;
    }
  }

  watch(query, () => {
    mode.value = "all";
  }, { flush: "sync" });

  watch([query, mode], () => {
    requestId++;
    error.value = "";
    recipes.value = [];
    loading.value = false;
  }, { flush: "sync" });

  watchDebounced([query, mode], searchRecipes, { debounce: 500 });

  return { query, mode, error, loading, data: recipes, trigger: searchRecipes };
}
