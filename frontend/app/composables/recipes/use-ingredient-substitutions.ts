import type { IngredientFood, IngredientFoodSubstitution, RecipeIngredient } from "~/lib/api/types/recipe";

/**
 * Splits an ingredient's substitutions into the two tiers the UI shows separately: the ones
 * this recipe declares for this line, and the ones the food carries everywhere it is used.
 *
 * Both tiers have the same {substituteFood, note} shape, so callers can render them alike.
 */
export function useIngredientSubstitutions(ingredient: () => RecipeIngredient) {
  const recipeSubstitutions = computed(() => ingredient().substitutions || []);

  const foodSubstitutions = computed<IngredientFoodSubstitution[]>(() => {
    // the food is typed as a read-or-create union because either shape is accepted on input;
    // an ingredient that came back from the API always carries the read shape
    const food = ingredient().food as IngredientFood | null | undefined;
    return food?.substitutions || [];
  });

  const hasSubstitutions = computed(() => !!recipeSubstitutions.value.length || !!foodSubstitutions.value.length);

  return { recipeSubstitutions, foodSubstitutions, hasSubstitutions };
}
