import { computed, useContext } from "@nuxtjs/composition-api";
import { Recipe } from "~/lib/api/types/recipe";
import { useLoggedInState } from "~/composables/use-logged-in-state";

export function useRecipePermissions(recipe: Recipe) {
    const { $auth } = useContext();
    const user = $auth.user;

    const { isOwnGroup } = useLoggedInState();

    const canEditRecipe = computed(() => {
        // Check recipe owner
        if (!user?.id) {
          return false;
        }
        if (user.id === recipe.userId) {
          return true;
        }

        // Check group and household
        if (!isOwnGroup.value) {
          return false;
        }
        if (user.householdId !== recipe.householdId) {
          return false;
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
