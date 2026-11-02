import type { ShoppingListOut } from "~/lib/api/types/household";
import { useUserApi } from "~/composables/api";
import { useFoodStore } from "~/composables/store";
import { alert } from "~/composables/use-toast";

/**
 * Composable for marking the foods of checked shopping list items as on hand for the user's household
 */
export function useShoppingListOnHand(shoppingList: Ref<ShoppingListOut | null>) {
  const i18n = useI18n();
  const userApi = useUserApi();
  const foodStore = useFoodStore();

  async function markCheckedItemsOnHand() {
    const checked = shoppingList.value?.listItems?.filter(item => item.checked) ?? [];
    if (!checked.length) {
      return;
    }

    // only items linked to a food can be marked, and several items can share the same food
    const foodIds = [...new Set(checked.map(item => item.foodId).filter((id): id is string => !!id))];
    const skipped = checked.filter(item => !item.foodId).length;

    if (!foodIds.length) {
      alert.info(i18n.t("shopping-list.no-checked-items-have-a-food"));
      return;
    }

    const { error } = await userApi.households.addFoodsOnHand(foodIds);
    if (error) {
      // the API client has already shown the error
      return;
    }

    // the food store caches each food's on hand status, so refresh it for the pages that show it
    foodStore.actions.refresh();

    const messages = [i18n.t("shopping-list.marked-foods-on-hand", foodIds.length)];
    if (skipped) {
      messages.push(i18n.t("shopping-list.checked-items-without-food-skipped", skipped));
    }
    alert.success(messages.join(" "));
  }

  return {
    markCheckedItemsOnHand,
  };
}
