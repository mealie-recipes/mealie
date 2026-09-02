import type { IngredientFood, IngredientFoodSubstitution, RecipeIngredient } from "~/lib/api/types/recipe";

// the food is typed as a read-or-create union because either shape is accepted on input;
// an ingredient that came back from the API always carries the read shape
function foodSubstitutionsOf(ingredient: RecipeIngredient): IngredientFoodSubstitution[] {
  const food = ingredient.food as IngredientFood | null | undefined;
  return food?.substitutions || [];
}

/**
 * Splits an ingredient's substitutions into the two tiers the UI shows separately: the ones
 * this recipe declares for this line, and the ones the food carries everywhere it is used.
 *
 * Both tiers have the same {substituteFood, note} shape, so callers can render them alike.
 */
export function useIngredientSubstitutions(ingredient: () => RecipeIngredient) {
  const recipeSubstitutions = computed(() => ingredient().substitutions || []);
  const foodSubstitutions = computed(() => foodSubstitutionsOf(ingredient()));
  const hasSubstitutions = computed(() => !!recipeSubstitutions.value.length || !!foodSubstitutions.value.length);

  return { recipeSubstitutions, foodSubstitutions, hasSubstitutions };
}

/**
 * Both tiers flattened into one line, recipe-level first, for surfaces that have no room for
 * the two-section treatment and nothing to click -- print, above all.
 *
 * Returns "" when there are none, which is also the "don't render a line" signal.
 */
export function ingredientSubstitutionSummary(ingredient: RecipeIngredient): string {
  return [...(ingredient.substitutions || []), ...foodSubstitutionsOf(ingredient)]
    .map((substitution) => {
      const food = substitution.substituteFood?.name;
      if (food && substitution.note) {
        return `${food} (${substitution.note})`;
      }
      // either half stands alone, the same way it does on screen
      return food || substitution.note || "";
    })
    .filter(Boolean)
    .join(", ");
}
