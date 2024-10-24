import { useAsync, useRouter, ref } from "@nuxtjs/composition-api";
import { useAsyncKey } from "../use-utils";
import { usePublicExploreApi } from "~/composables/api/api-client";
import { useUserApi } from "~/composables/api";
import { Recipe } from "~/lib/api/types/recipe";
import { RecipeSearchQuery } from "~/lib/api/user/recipes/recipe";

export const allRecipes = ref<Recipe[]>([]);
export const recentRecipes = ref<Recipe[]>([]);

function getParams(
  orderBy: string | null = null,
  orderDirection = "desc",
  query: RecipeSearchQuery | null = null,
  queryFilter: string | null = null
) {
  return {
    orderBy,
    orderDirection,
    paginationSeed: query?._searchSeed, // propagate searchSeed to stabilize random order pagination
    searchSeed: query?._searchSeed, // unused, but pass it along for completeness of data
    search: query?.search,
    cookbook: query?.cookbook,
    households: query?.households,
    categories: query?.categories,
    requireAllCategories: query?.requireAllCategories,
    tags: query?.tags,
    requireAllTags: query?.requireAllTags,
    tools: query?.tools,
    requireAllTools: query?.requireAllTools,
    foods: query?.foods,
    requireAllFoods: query?.requireAllFoods,
    queryFilter,
  };
};

export const useLazyRecipes = function (publicGroupSlug: string | null = null) {
  const router = useRouter();

  // passing the group slug switches to using the public API
  const api = publicGroupSlug ? usePublicExploreApi(publicGroupSlug).explore : useUserApi();

  const recipes = ref<Recipe[]>([]);

  async function fetchMore(
    page: number,
    perPage: number,
    orderBy: string | null = null,
    orderDirection = "desc",
    query: RecipeSearchQuery | null = null,
    queryFilter: string | null = null,
  ) {

    const { data, error } = await api.recipes.getAll(
      page,
      perPage,
      getParams(orderBy, orderDirection, query, queryFilter),
    );

    if (error?.response?.status === 404) {
      router.push("/login");
    }

    return data ? data.items : [];
  }

  function appendRecipes(val: Array<Recipe>) {
    val.forEach((recipe) => {
      recipes.value.push(recipe);
    });
  }

  function assignSorted(val: Array<Recipe>) {
    recipes.value = val;
  }

  function removeRecipe(slug: string) {
    for (let i = 0; i < recipes?.value?.length; i++) {
      if (recipes?.value[i].slug === slug) {
        recipes?.value.splice(i, 1);
        break;
      }
    }
  }

  function replaceRecipes(val: Array<Recipe>) {
    recipes.value = val;
  }

  async function getRandom(query: RecipeSearchQuery | null = null, queryFilter: string | null = null) {
    const { data } = await api.recipes.getAll(1, 1, getParams("random", "desc", query, queryFilter));
    if (data?.items.length) {
      return data.items[0];
    }
  }

  return {
    recipes,
    fetchMore,
    appendRecipes,
    assignSorted,
    removeRecipe,
    replaceRecipes,
    getRandom,
  };
};

export const useRecipes = (
  all = false,
  fetchRecipes = true,
  loadFood = false,
  queryFilter: string | null = null,
  publicGroupSlug: string | null = null
) => {
  const api = publicGroupSlug ? usePublicExploreApi(publicGroupSlug).explore : useUserApi();

  // recipes is non-reactive!!
  const { recipes, page, perPage } = (() => {
    if (all) {
      return {
        recipes: allRecipes,
        page: 1,
        perPage: -1,
      };
    } else {
      return {
        recipes: recentRecipes,
        page: 1,
        perPage: 30,
      };
    }
  })();

  async function refreshRecipes() {
    const { data } = await api.recipes.getAll(page, perPage, { loadFood, orderBy: "created_at", queryFilter });
    if (data) {
      recipes.value = data.items;
    }
  }

  function getAllRecipes() {
    useAsync(async () => {
      await refreshRecipes();
    }, useAsyncKey());
  }

  function assignSorted(val: Array<Recipe>) {
    recipes.value = val;
  }

  if (fetchRecipes) {
    getAllRecipes();
  }

  return { getAllRecipes, assignSorted, refreshRecipes };
};
