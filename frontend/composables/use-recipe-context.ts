import {  useAsync, ref } from "@nuxtjs/composition-api";
import { useApiSingleton } from "~/composables/use-api";
import { Recipe } from "~/types/api-types/recipe";

export const useRecipeContext = function () {
  const api = useApiSingleton();
  const loading = ref(false)


  function getBySlug(slug: string) {
    loading.value = true
    const recipe = useAsync(async () => {
      const { data } = await api.recipes.getOne(slug);
      return data;
    }, slug);

    loading.value = false

    return recipe;
  }

  async function  deleteRecipe(slug: string) {
    loading.value = true
    const { data } = await api.recipes.deleteOne(slug);
    loading.value = false
    return data;
  }

  async function updateRecipe(slug: string, recipe: Recipe) {
    loading.value = true
    const { data } = await api.recipes.updateOne(slug, recipe);
    loading.value = false
    return data;
  }


  return {loading, getBySlug, deleteRecipe, updateRecipe}
};
