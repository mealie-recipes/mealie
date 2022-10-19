import { useAsync, ref } from "@nuxtjs/composition-api";
import { useAsyncKey } from "../use-utils";
import { useUserApi } from "~/composables/api";
import { Recipe } from "~/lib/api/types/recipe";

export const allRecipes = ref<Recipe[]>([]);
export const recentRecipes = ref<Recipe[]>([]);

export const useLazyRecipes = function () {
  const api = useUserApi();

  const recipes = ref<Recipe[]>([]);

  async function fetchMore(
    page: number,
    perPage: number,
    orderBy: string | null = null,
    orderDirection = "desc",
    cookbook: string | null = null,
    category: string | null = null,
    tag: string | null = null,
    tool: string | null = null
  ) {
    const { data } = await api.recipes.getAll(page, perPage, {
      orderBy,
      orderDirection,
      cookbook,
      categories: category,
      tags: tag,
      tools: tool,
    });
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

  return {
    recipes,
    fetchMore,
    appendRecipes,
    assignSorted,
    removeRecipe,
    replaceRecipes,
  };
};

export const useRecipes = (all = false, fetchRecipes = true) => {
  const api = useUserApi();

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
    const { data } = await api.recipes.getAll(page, perPage, { loadFood: true, orderBy: "created_at" });
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
