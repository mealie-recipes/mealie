import { computed, ref, toValue } from "vue";
import type { MaybeRefOrGetter } from "vue";
import { useUserApi } from "~/composables/api";
import type { CreateIngredientFood, Recipe } from "~/lib/api/types/recipe";

/**
 * Lists the foods in a recipe that a household has on hand, so after making the recipe
 * the user can pick the ones they used up and remove them from On Hand
 */
export function useRecipeOnHandFoods(
  recipe: MaybeRefOrGetter<Recipe>,
  householdSlug: MaybeRefOrGetter<string | undefined>,
) {
  const userApi = useUserApi();

  const usedUpFoodIds = ref<string[]>([]);

  // the recipe's food data isn't reloaded after a removal, so keep track of what was removed
  const removedFoodIds = ref<string[]>([]);

  const onHandFoods = computed(() => {
    const slug = toValue(householdSlug);
    if (!slug) {
      return [];
    }

    // several ingredients can use the same food, so list each food once
    const foodNames = new Map<string, string>();
    for (const ingredient of toValue(recipe).recipeIngredient ?? []) {
      const food: CreateIngredientFood | null | undefined = ingredient.food;
      if (
        food?.id
        && food.householdsWithIngredientFood?.includes(slug)
        && !removedFoodIds.value.includes(food.id)
      ) {
        foodNames.set(food.id, food.name);
      }
    }

    return [...foodNames].map(([id, name]) => ({ id, name }));
  });

  /** Removes the used-up foods from On Hand. Returns false if the request failed. */
  async function removeUsedUpFoods() {
    const foodIds = [...usedUpFoodIds.value];
    if (!foodIds.length) {
      return true;
    }

    const { error } = await userApi.households.removeFoodsOnHand(foodIds);
    if (error) {
      return false;
    }

    removedFoodIds.value.push(...foodIds);
    usedUpFoodIds.value = [];
    return true;
  }

  function resetUsedUpFoods() {
    usedUpFoodIds.value = [];
  }

  return {
    onHandFoods,
    usedUpFoodIds,
    removeUsedUpFoods,
    resetUsedUpFoods,
  };
}
