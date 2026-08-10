import type { Recipe } from "~/lib/api/types/recipe";
import type { HouseholdInDB } from "~/lib/api/types/household";
import type { GroupSummary } from "~/lib/api/types/user";

export function isRecipeFullyPublic(
  recipe: Recipe | null | undefined,
  group: GroupSummary | null | undefined,
  household: HouseholdInDB | null | undefined,
): boolean {
  return (
    recipe?.groupId === group?.id
    && recipe?.householdId === household?.id
    && recipe?.settings?.public === true
    && group?.preferences?.privateGroup === false
    && household?.preferences?.privateHousehold === false
  );
}
