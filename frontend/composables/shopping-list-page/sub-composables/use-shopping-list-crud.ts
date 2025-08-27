import type { ShoppingListOut, ShoppingListItemOut, ShoppingListMultiPurposeLabelOut } from "~/lib/api/types/household";
import { useUserApi } from "~/composables/api";
import { uuid4 } from "~/composables/use-utils";

/**
 * Composable for managing shopping list item CRUD operations
 */
export function useShoppingListCrud(
  shoppingList: Ref<ShoppingListOut | null>,
  loadingCounter: Ref<number>,
  listItems: { unchecked: ShoppingListItemOut[]; checked: ShoppingListItemOut[] },
  shoppingListItemActions: any,
  refresh: () => void,
  sortCheckedItems: (a: ShoppingListItemOut, b: ShoppingListItemOut) => number,
  updateListItemOrder: () => void,
) {
  const { t } = useI18n();
  const userApi = useUserApi();

  const createListItemData = ref<ShoppingListItemOut>(listItemFactory());
  const localLabels = ref<ShoppingListMultiPurposeLabelOut[]>();

  function listItemFactory(): ShoppingListItemOut {
    return {
      id: uuid4(),
      shoppingListId: shoppingList.value?.id || "",
      checked: false,
      position: shoppingList.value?.listItems?.length || 1,
      quantity: 0,
      note: "",
      labelId: undefined,
      unitId: undefined,
      foodId: undefined,
    } as ShoppingListItemOut;
  }

  // Check/Uncheck All operations
  function checkAllItems() {
    let hasChanged = false;
    shoppingList.value?.listItems?.forEach((item) => {
      if (!item.checked) {
        hasChanged = true;
        item.checked = true;
      }
    });
    if (hasChanged) {
      updateUncheckedListItems();
    }
  }

  function uncheckAllItems() {
    let hasChanged = false;
    shoppingList.value?.listItems?.forEach((item) => {
      if (item.checked) {
        hasChanged = true;
        item.checked = false;
      }
    });
    if (hasChanged) {
      listItems.unchecked = [...listItems.unchecked, ...listItems.checked];
      listItems.checked = [];
      updateUncheckedListItems();
    }
  }

  function deleteCheckedItems() {
    const checked = shoppingList.value?.listItems?.filter(item => item.checked);

    if (!checked || checked?.length === 0) {
      return;
    }

    loadingCounter.value += 1;
    deleteListItems(checked);
    loadingCounter.value -= 1;
    refresh();
  }

  function saveListItem(item: ShoppingListItemOut) {
    if (!shoppingList.value) {
      return;
    }

    // set a temporary updatedAt timestamp prior to refresh so it appears at the top of the checked items
    item.updatedAt = new Date().toISOString();

    // make updates reflect immediately
    if (shoppingList.value.listItems) {
      shoppingList.value.listItems.forEach((oldListItem: ShoppingListItemOut, idx: number) => {
        if (oldListItem.id === item.id && shoppingList.value?.listItems) {
          shoppingList.value.listItems[idx] = item;
        }
      });
      // Immediately update checked/unchecked arrays for UI
      listItems.unchecked = shoppingList.value.listItems.filter(i => !i.checked);
      listItems.checked = shoppingList.value.listItems.filter(i => i.checked)
        .sort(sortCheckedItems);
    }

    // Update the item if it's checked, otherwise updateUncheckedListItems will handle it
    if (item.checked) {
      shoppingListItemActions.updateItem(item);
    }

    updateListItemOrder();
    updateUncheckedListItems();
  }

  function deleteListItem(item: ShoppingListItemOut) {
    if (!shoppingList.value) {
      return;
    }

    shoppingListItemActions.deleteItem(item);

    // remove the item from the list immediately so the user sees the change
    if (shoppingList.value.listItems) {
      shoppingList.value.listItems = shoppingList.value.listItems.filter(itm => itm.id !== item.id);
    }

    refresh();
  }

  function deleteListItems(items: ShoppingListItemOut[]) {
    if (!shoppingList.value) {
      return;
    }

    items.forEach((item) => {
      shoppingListItemActions.deleteItem(item);
    });
    // remove the items from the list immediately so the user sees the change
    if (shoppingList.value?.listItems) {
      const deletedItems = new Set(items.map(item => item.id));
      shoppingList.value.listItems = shoppingList.value.listItems.filter(itm => !deletedItems.has(itm.id));
    }

    refresh();
  }

  function createListItem() {
    if (!shoppingList.value) {
      return;
    }

    if (!createListItemData.value.foodId && !createListItemData.value.note) {
      // don't create an empty item
      return;
    }

    loadingCounter.value += 1;

    // ensure list id is set to the current list, which may not have loaded yet in the factory
    createListItemData.value.shoppingListId = shoppingList.value.id;

    // ensure item is inserted into the end of the list, which may have been updated
    createListItemData.value.position = shoppingList.value?.listItems?.length
      ? (shoppingList.value.listItems.reduce((a, b) => (a.position || 0) > (b.position || 0) ? a : b).position || 0) + 1
      : 0;

    createListItemData.value.createdAt = new Date().toISOString();
    createListItemData.value.updatedAt = createListItemData.value.createdAt;

    updateListItemOrder();

    shoppingListItemActions.createItem(createListItemData.value);
    loadingCounter.value -= 1;

    if (shoppingList.value.listItems) {
      // add the item to the list immediately so the user sees the change
      shoppingList.value.listItems.push(createListItemData.value);
      updateListItemOrder();
    }
    createListItemData.value = listItemFactory();
    refresh();
  }

  function updateUncheckedListItems() {
    if (!shoppingList.value?.listItems) {
      return;
    }

    // Set position for unchecked items
    listItems.unchecked.forEach((item: ShoppingListItemOut, idx: number) => {
      item.position = idx;
      shoppingListItemActions.updateItem(item);
    });

    refresh();
  }

  // Label management
  function updateLabelOrder(labelSettings: ShoppingListMultiPurposeLabelOut[]) {
    if (!shoppingList.value) {
      return;
    }

    labelSettings.forEach((labelSetting, index) => {
      labelSetting.position = index;
      return labelSetting;
    });

    localLabels.value = labelSettings;
  }

  function cancelLabelOrder() {
    loadingCounter.value -= 1;
    if (!shoppingList.value) {
      return;
    }
    // restore original state
    localLabels.value = shoppingList.value.labelSettings;
  }

  async function saveLabelOrder(updateItemsByLabel: () => void) {
    if (!shoppingList.value || !localLabels.value || (localLabels.value === shoppingList.value.labelSettings)) {
      return;
    }

    loadingCounter.value += 1;
    const { data } = await userApi.shopping.lists.updateLabelSettings(shoppingList.value.id, localLabels.value);
    loadingCounter.value -= 1;

    if (data) {
      // update shoppingList labels using the API response
      shoppingList.value.labelSettings = (data as ShoppingListOut).labelSettings;
      updateItemsByLabel();
    }
  }

  function toggleReorderLabelsDialog(reorderLabelsDialog: Ref<boolean>) {
    // stop polling and populate localLabels
    loadingCounter.value += 1;
    reorderLabelsDialog.value = !reorderLabelsDialog.value;
    localLabels.value = shoppingList.value?.labelSettings;
  }

  // Context menu actions
  const contextActions = {
    delete: "delete",
  };

  const contextMenu = [
    { title: t("general.delete"), action: contextActions.delete },
  ];

  return {
    createListItemData,
    localLabels,
    listItemFactory,
    checkAllItems,
    uncheckAllItems,
    deleteCheckedItems,
    saveListItem,
    deleteListItem,
    deleteListItems,
    createListItem,
    updateUncheckedListItems,
    updateLabelOrder,
    cancelLabelOrder,
    saveLabelOrder,
    toggleReorderLabelsDialog,
    contextActions,
    contextMenu,
  };
}
