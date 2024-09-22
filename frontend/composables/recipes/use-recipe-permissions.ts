import { computed, Ref } from "@nuxtjs/composition-api";
import { Recipe } from "~/lib/api/types/recipe";
import { HouseholdSummary } from "~/lib/api/types/household";
import { UserOut } from "~/lib/api/types/user";

export function useRecipePermissions(
  recipe: Recipe,
  recipeHousehold: Ref<HouseholdSummary | undefined>,
  user: UserOut | null,
) {
  const canEditRecipe = computed(() => {
    // Check recipe owner
    if (!user?.id) {
      return false;
    }
    if (user.id === recipe.userId) {
      return true;
    }

    // Check group and household
    if (user.groupId !== recipe.groupId) {
      return false;
    }
    if (user.householdId !== recipe.householdId) {
      if (!recipeHousehold.value?.preferences) {
        return false;
      }
      if (recipeHousehold.value?.preferences.lockRecipeEditsFromOtherHouseholds) {
        return false;
      }
    }

    // Check recipe
    if (recipe.settings?.locked) {
      return false;
    }

    return true;
  });

  return {
    canEditRecipe,
  }
}
