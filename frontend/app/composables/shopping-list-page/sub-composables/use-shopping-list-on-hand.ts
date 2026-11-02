import type { ShoppingListItemOut, ShoppingListOut } from "~/lib/api/types/household";
import { useUserApi } from "~/composables/api";
import { alert } from "~/composables/use-toast";

/**
 * Composable for marking the foods of checked shopping list items as on hand for the user's household,
 * then removing those items from the list
 */
export function useShoppingListOnHand(
  shoppingList: Ref<ShoppingListOut | null>,
  deleteListItems: (items: ShoppingListItemOut[]) => void,
) {
  const i18n = useI18n();
  const userApi = useUserApi();

  async function markCheckedItemsOnHand() {
    const checked = shoppingList.value?.listItems?.filter(item => item.checked) ?? [];
    if (!checked.length) {
      return;
    }

    // only items linked to a food can be marked, and several items can share the same food
    const itemsWithFood = checked.filter(item => !!item.foodId);
    const foodIds = [...new Set(itemsWithFood.map(item => item.foodId).filter((id): id is string => !!id))];
    const skipped = checked.length - itemsWithFood.length;

    if (!foodIds.length) {
      alert.info(i18n.t("shopping-list.no-checked-items-have-a-food"));
      return;
    }

    const { error } = await userApi.households.addFoodsOnHand(foodIds);
    if (error) {
      // the API client has already shown the error, and the items stay on the list
      return;
    }

    // the marked items are now recorded as on hand, so they leave the list; items without
    // a food stay, since nothing recorded them
    deleteListItems(itemsWithFood);

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
