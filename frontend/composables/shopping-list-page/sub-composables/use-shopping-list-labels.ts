import { useToggle } from "@vueuse/core";
import type { ShoppingListOut, ShoppingListItemOut } from "~/lib/api/types/household";

/**
 * Composable for managing shopping list label state and operations
 */
export function useShoppingListLabels(shoppingList: Ref<ShoppingListOut | null>) {
  const { t } = useI18n();
  const labelOpenState = ref<{ [key: string]: boolean }>({});
  const [showChecked, toggleShowChecked] = useToggle(false);

  const initializeLabelOpenStates = () => {
    if (!shoppingList.value?.listItems) return;

    const existingLabels = new Set(Object.keys(labelOpenState.value));
    let hasChanges = false;

    for (const item of shoppingList.value.listItems) {
      const labelName = item.label?.name || t("shopping-list.no-label");
      if (!existingLabels.has(labelName) && !(labelName in labelOpenState.value)) {
        labelOpenState.value[labelName] = true;
        hasChanges = true;
      }
    }

    if (hasChanges) {
      labelOpenState.value = { ...labelOpenState.value };
    }
  };

  const labelNames = computed(() => {
    return new Set(
      shoppingList.value?.listItems
        ?.map(item => item.label?.name || t("shopping-list.no-label"))
        .filter(Boolean) ?? [],
    );
  });

  watch(labelNames, initializeLabelOpenStates, { immediate: true });

  function toggleShowLabel(key: string) {
    labelOpenState.value[key] = !labelOpenState.value[key];
  }

  function getLabelColor(item: ShoppingListItemOut | null) {
    return item?.label?.color;
  }

  const presentLabels = computed(() => {
    const labels: Array<{ id: string; name: string }> = [];

    shoppingList.value?.listItems?.forEach((item) => {
      if (item.labelId && item.label) {
        labels.push({
          name: item.label.name,
          id: item.labelId,
        });
      }
    });

    return labels;
  });

  return {
    labelOpenState,
    showChecked,
    toggleShowChecked,
    toggleShowLabel,
    getLabelColor,
    presentLabels,
    initializeLabelOpenStates,
  };
}
