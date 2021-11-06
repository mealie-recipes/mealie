import { ref, onMounted } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { Recipe } from "~/types/api-types/recipe";

export const useRecipe = function (slug: string, eager: boolean = true) {
  const api = useUserApi();
  const loading = ref(false);

  const recipe = ref<Recipe | null>(null);

  async function fetchRecipe() {
    loading.value = true;
    const { data } = await api.recipes.getOne(slug);
    loading.value = false;
    if (data) {
      recipe.value = data;
    }
  }

  async function deleteRecipe() {
    loading.value = true;
    const { data } = await api.recipes.deleteOne(slug);
    loading.value = false;
    return data;
  }

  async function updateRecipe(recipe: Recipe) {
    loading.value = true;
    const { data } = await api.recipes.updateOne(slug, recipe);
    loading.value = false;
    return data;
  }

  onMounted(() => {
    if (eager) {
      fetchRecipe();
    }
  });

  return {
    recipe,
    loading,
    fetchRecipe,
    deleteRecipe,
    updateRecipe,
  };
};
