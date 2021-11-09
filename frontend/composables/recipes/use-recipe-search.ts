import { computed, reactive, ref, Ref } from "@nuxtjs/composition-api";
import Fuse from "fuse.js";
import { Recipe } from "~/types/api-types/recipe";

export const useRecipeSearch = (recipes: Ref<Recipe[] | null>) => {
  const localState = reactive({
    options: {
      shouldSort: true,
      threshold: 0.6,
      location: 0,
      distance: 100,
      findAllMatches: true,
      maxPatternLength: 32,
      minMatchCharLength: 2,
      keys: ["name", "description", "recipeIngredient.note", "recipeIngredient.food.name"],
    },
  });

  const search = ref("");

  const fuse = computed(() => {
    return new Fuse(recipes.value || [], localState.options);
  });

  const fuzzyRecipes = computed(() => {
    if (search.value.trim() === "") {
      return recipes.value;
    }
    const result = fuse.value.search(search.value.trim());
    return result.map((x) => x.item);
  });

  const results = computed(() => {
    if (!fuzzyRecipes.value) {
      return [];
    }

    if (fuzzyRecipes.value.length > 0 && search.value.length != null && search.value.length >= 1) {
      return fuzzyRecipes.value;
    } else {
      return recipes.value;
    }
  });

  return { results, search };
};
