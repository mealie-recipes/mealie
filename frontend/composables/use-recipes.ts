import { useAsync, ref } from "@nuxtjs/composition-api";
import { set } from "@vueuse/core";
import { useAsyncKey } from "./use-utils";
import { useApiSingleton } from "~/composables/use-api";
import { Recipe } from "~/types/api-types/recipe";

export const allRecipes = ref<Recipe[] | null>([]);
export const recentRecipes = ref<Recipe[] | null>([]);

export const useRecipes = (all = false, fetchRecipes = true) => {
  const api = useApiSingleton();

  // recipes is non-reactive!!
  const { recipes, start, end } = (() => {
    if (all) {
      return {
        recipes: allRecipes,
        start: 0,
        end: 9999,
      };
    } else {
      return {
        recipes: recentRecipes,
        start: 0,
        end: 30,
      };
    }
  })();

  async function refreshRecipes() {
    const { data } = await api.recipes.getAll(start, end);
    if (data) {
      set(recipes, data);
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

  return { getAllRecipes, assignSorted };
};
