import type { ShoppingListItemOut } from "~/lib/api/types/household";
import { useShoppingListState } from "~/composables/shopping-list-page/sub-composables/use-shopping-list-state";
import { useShoppingListData } from "~/composables/shopping-list-page/sub-composables/use-shopping-list-data";
import { useShoppingListSorting } from "~/composables/shopping-list-page/sub-composables/use-shopping-list-sorting";
import { useShoppingListLabels } from "~/composables/shopping-list-page/sub-composables/use-shopping-list-labels";
import { useShoppingListCopy } from "~/composables/shopping-list-page/sub-composables/use-shopping-list-copy";
import { useShoppingListCrud } from "~/composables/shopping-list-page/sub-composables/use-shopping-list-crud";
import { useShoppingListRecipes } from "~/composables/shopping-list-page/sub-composables/use-shopping-list-recipes";

/**
 * Main composable that orchestrates all shopping list page functionality
 */
export function useShoppingListPage(listId: string) {
  // Initialize state
  const state = useShoppingListState();
  const {
    shoppingList,
    loadingCounter,
    recipeReferenceLoading,
    preserveItemOrder,
    listItems,
    sortCheckedItems,
  } = state;

  // Initialize sorting functionality
  const sorting = useShoppingListSorting();
  const { groupAndSortListItemsByFood, sortListItems, updateItemsByLabel } = sorting;

  // Track items organized by label
  const itemsByLabel = ref<{ [key: string]: ShoppingListItemOut[] }>({});

  function updateListItemOrder() {
    if (!shoppingList.value) return;

    if (!preserveItemOrder.value) {
      groupAndSortListItemsByFood(shoppingList.value);
    }
    else {
      sortListItems(shoppingList.value);
    }

    const labeledItems = updateItemsByLabel(shoppingList.value);
    if (labeledItems) {
      itemsByLabel.value = labeledItems;
    }
  }

  // Initialize data management
  const dataManager = useShoppingListData(listId, shoppingList, loadingCounter);
  const { isOffline, refresh: baseRefresh, startPolling, stopPolling, shoppingListItemActions } = dataManager;

  const refresh = () => baseRefresh(updateListItemOrder);

  // Initialize shopping list labels
  const labels = useShoppingListLabels(shoppingList);

  // Initialize copy functionality
  const copyManager = useShoppingListCopy();

  // Initialize CRUD operations
  const crud = useShoppingListCrud(
    shoppingList,
    loadingCounter,
    listItems,
    shoppingListItemActions,
    refresh,
    sortCheckedItems,
    updateListItemOrder,
  );

  // Initialize recipe management
  const recipes = useShoppingListRecipes(
    shoppingList,
    loadingCounter,
    recipeReferenceLoading,
    refresh,
  );

  // Handle item reordering by label
  function updateIndexUncheckedByLabel(labelName: string, labeledUncheckedItems: ShoppingListItemOut[]) {
    if (!itemsByLabel.value[labelName]) {
      return;
    }

    // update this label's item order
    itemsByLabel.value[labelName] = labeledUncheckedItems;

    // reset list order of all items
    const allUncheckedItems: ShoppingListItemOut[] = [];
    for (const labelKey in itemsByLabel.value) {
      allUncheckedItems.push(...itemsByLabel.value[labelKey]);
    }

    // since the user has manually reordered the list, we should preserve this order
    preserveItemOrder.value = true;

    // save changes
    listItems.unchecked = allUncheckedItems;
    listItems.checked = shoppingList.value?.listItems?.filter(item => item.checked) || [];
    crud.updateUncheckedListItems();
  }

  // Dialog helpers
  function openCheckAll() {
    if (shoppingList.value?.listItems?.some(item => !item.checked)) {
      state.state.checkAllDialog = true;
    }
  }

  function openUncheckAll() {
    if (shoppingList.value?.listItems?.some(item => item.checked)) {
      state.state.uncheckAllDialog = true;
    }
  }

  function openDeleteChecked() {
    if (shoppingList.value?.listItems?.some(item => item.checked)) {
      state.state.deleteCheckedDialog = true;
    }
  }

  function checkAll() {
    state.state.checkAllDialog = false;
    crud.checkAllItems();
  }

  function uncheckAll() {
    state.state.uncheckAllDialog = false;
    crud.uncheckAllItems();
  }

  function deleteChecked() {
    state.state.deleteCheckedDialog = false;
    crud.deleteCheckedItems();
  }

  // Copy functionality wrapper
  function copyListItems(copyType: "plain" | "markdown") {
    copyManager.copyListItems(itemsByLabel.value, copyType);
  }

  // Label reordering helpers
  function toggleReorderLabelsDialog() {
    crud.toggleReorderLabelsDialog(state.reorderLabelsDialog);
  }

  async function saveLabelOrder() {
    await crud.saveLabelOrder(() => {
      const labeledItems = updateItemsByLabel(shoppingList.value!);
      if (labeledItems) {
        itemsByLabel.value = labeledItems;
      }
    });
  }

  // Lifecycle management
  onMounted(() => {
    startPolling(updateListItemOrder);
  });

  onUnmounted(() => {
    stopPolling();
  });

  return {
    itemsByLabel,
    isOffline,

    // Sub-composables
    ...state,
    ...labels,
    ...crud,
    ...recipes,

    // Specialized functions
    updateIndexUncheckedByLabel,
    copyListItems,

    // Dialog actions
    openCheckAll,
    openUncheckAll,
    openDeleteChecked,
    checkAll,
    uncheckAll,
    deleteChecked,

    // Label management
    toggleReorderLabelsDialog,
    saveLabelOrder,

    // Data refresh
    refresh,
  };
}
