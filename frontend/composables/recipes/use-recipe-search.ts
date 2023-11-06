import { Ref, ref } from "@nuxtjs/composition-api";
import { watchDebounced } from "@vueuse/core";
import { UserApi } from "~/lib/api";
import { ExploreApi } from "~/lib/api/public/explore";
import { Recipe } from "~/lib/api/types/recipe";

export interface UseRecipeSearchReturn {
  query: Ref<string>;
  error: Ref<string>;
  loading: Ref<boolean>;
  data: Ref<Recipe[]>;
  trigger(): Promise<void>;
}

/**
 * `useRecipeSearch` constructs a basic reactive search query
 * that when `query` is changed, will search for recipes based
 * on the query. Useful for searchable list views. For advanced
 * search, use the `useRecipeQuery` composable.
 */
export function useRecipeSearch(api: UserApi | ExploreApi): UseRecipeSearchReturn {
  const query = ref("");
  const error = ref("");
  const loading = ref(false);
  const recipes = ref<Recipe[]>([]);

  async function searchRecipes(term: string) {
    loading.value = true;
    const { data, error } = await api.recipes.search({
      search: term,
      page: 1,
      orderBy: "name",
      orderDirection: "asc",
      perPage: 20,
      _searchSeed: Date.now().toString(),
    });

    if (error) {
      console.error(error);
      loading.value = false;
      recipes.value = [];
      return;
    }

    if (data) {
      recipes.value = data.items;
    }

    loading.value = false;
  }

  watchDebounced(
    () => query.value,
    async (term: string) => {
      await searchRecipes(term);
    },
    { debounce: 500 }
  );

  async function trigger() {
    await searchRecipes(query.value);
  }

  return {
    query,
    error,
    loading,
    data: recipes,
    trigger,
  };
}
