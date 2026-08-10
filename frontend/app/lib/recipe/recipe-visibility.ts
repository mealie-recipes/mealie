import type { Recipe } from "~/lib/api/types/recipe";
import type { HouseholdSummary } from "~/lib/api/types/household";
import type { GroupSummary } from "~/lib/api/types/user";

/**
 * Whether a recipe is reachable by anyone with its link, without a share token.
 *
 * This mirrors the checks the backend makes when serving a recipe to an anonymous
 * user (see `/api/explore/groups/{group_slug}/recipes/{recipe_slug}`):
 * the recipe's group must be public, the recipe's *own* household must be public,
 * and the recipe itself must be marked public.
 *
 * `recipeHousehold` must be the household the recipe belongs to, not the current
 * user's household; a recipe may live in another household of the same group.
 */
export function isRecipeFullyPublic(
  recipe: Recipe | null | undefined,
  group: GroupSummary | null | undefined,
  recipeHousehold: HouseholdSummary | null | undefined,
): boolean {
  if (!recipe || !group || !recipeHousehold) {
    return false;
  }

  // the preferences we were handed have to be the recipe's, otherwise we're checking nothing
  if (recipe.groupId !== group.id || recipe.householdId !== recipeHousehold.id) {
    return false;
  }

  return (
    group.preferences?.privateGroup === false
    && recipeHousehold.preferences?.privateHousehold === false
    && recipe.settings?.public === true
  );
}
