import { useAsync, ref } from "@nuxtjs/composition-api";
import { set } from "@vueuse/core";
import { useAsyncKey } from "../use-utils";
import { useUserApi } from "~/composables/api";
import { Recipe } from "~/types/api-types/recipe";

export const allRecipes = ref<Recipe[] | null>([]);
export const recentRecipes = ref<Recipe[] | null>([]);

const rand = (n: number) => Math.floor(Math.random() * n);

function swap(t: Array<any>, i: number, j: number) {
  const q = t[i];
  t[i] = t[j];
  t[j] = q;
  return t;
}

export const useSorter = () => {
  function sortAToZ(list: Array<Recipe>) {
    list.sort((a, b) => {
      const textA = a.name?.toUpperCase() ?? "";
      const textB = b.name?.toUpperCase() ?? "";
      return textA < textB ? -1 : textA > textB ? 1 : 0;
    });
  }
  function sortByCreated(list: Array<Recipe>) {
    list.sort((a, b) => ((a.dateAdded ?? "") > (b.dateAdded ?? "") ? -1 : 1));
  }
  function sortByUpdated(list: Array<Recipe>) {
    list.sort((a, b) => ((a.dateUpdated ?? "") > (b.dateUpdated ?? "") ? -1 : 1));
  }
  function sortByRating(list: Array<Recipe>) {
    list.sort((a, b) => ((a.rating ?? 0) > (b.rating ?? 0) ? -1 : 1));
  }

  function randomRecipe(list: Array<Recipe>): Recipe {
    return list[Math.floor(Math.random() * list.length)];
  }

  function shuffle(list: Array<Recipe>) {
    let last = list.length;
    let n;
    while (last > 0) {
      n = rand(last);
      swap(list, n, --last);
    }
  }

  return {
    sortAToZ,
    sortByCreated,
    sortByUpdated,
    sortByRating,
    randomRecipe,
    shuffle,
  };
};

export const useLazyRecipes = function () {
  const api = useUserApi();

  const recipes = ref<Recipe[] | null>([]);

  async function fetchMore(start: number, limit: number) {
    const { data } = await api.recipes.getAll(start, limit);
    if (data) {
      data.forEach((recipe) => {
        recipes.value?.push(recipe);
      });
    }
  }

  return {
    recipes,
    fetchMore,
  };
};

export const useRecipes = (all = false, fetchRecipes = true) => {
  const api = useUserApi();

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
      // @ts-ignore
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

  return { getAllRecipes, assignSorted, refreshRecipes };
};
