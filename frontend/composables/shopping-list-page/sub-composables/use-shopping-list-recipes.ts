import type { ShoppingListOut } from "~/lib/api/types/household";
import { useUserApi } from "~/composables/api";

/**
 * Composable for managing shopping list recipe references
 */
export function useShoppingListRecipes(
  shoppingList: Ref<ShoppingListOut | null>,
  loadingCounter: Ref<number>,
  recipeReferenceLoading: Ref<boolean>,
  refresh: () => void,
) {
  const userApi = useUserApi();

  async function addRecipeReferenceToList(recipeId: string) {
    if (!shoppingList.value || recipeReferenceLoading.value) {
      return;
    }

    loadingCounter.value += 1;
    recipeReferenceLoading.value = true;
    const { data } = await userApi.shopping.lists.addRecipes(shoppingList.value.id, [{ recipeId }]);
    recipeReferenceLoading.value = false;
    loadingCounter.value -= 1;

    if (data) {
      refresh();
    }
  }

  async function removeRecipeReferenceToList(recipeId: string) {
    if (!shoppingList.value || recipeReferenceLoading.value) {
      return;
    }

    loadingCounter.value += 1;
    recipeReferenceLoading.value = true;
    const { data } = await userApi.shopping.lists.removeRecipe(shoppingList.value.id, recipeId);
    recipeReferenceLoading.value = false;
    loadingCounter.value -= 1;

    if (data) {
      refresh();
    }
  }

  return {
    addRecipeReferenceToList,
    removeRecipeReferenceToList,
  };
}
