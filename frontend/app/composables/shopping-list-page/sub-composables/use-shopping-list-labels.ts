import type { ShoppingListOut } from "~/lib/api/types/household";
import type { MultiPurposeLabelSummary } from "~/lib/api/types/labels";

/**
 * Composable for managing shopping list label state and operations
 */
export function useShoppingListLabels(shoppingList: Ref<ShoppingListOut | null>) {
  const { t } = useI18n();

  const labelColorByName = computed(() => {
    return shoppingList.value?.listItems
      ?.map(({ label }) => label as MultiPurposeLabelSummary)
      .filter(label => label)
      .reduce((acc, label) => ({
        ...acc,
        [label.name || t("shopping-list.no-label")]: label.color,
      }), {}) ?? {};
  });

  function getLabelColor(label: string) {
    return labelColorByName.value[label];
  }

  return {
    getLabelColor,
  };
}
